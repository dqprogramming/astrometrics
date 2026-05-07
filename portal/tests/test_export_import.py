"""Round-trip tests for the export_content / import_content commands.

Builds a representative slice of cms/portal/files data, exports it to a zip,
deletes everything in scope, imports the zip, then asserts that scalars,
foreign keys, content types, media files, and PK sequences all survive.
"""

import io
import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from cms.models import (
    BlockPage,
    Category,
    HeaderSettings,
    MembersHeaderBlock,
    MenuItem,
    Page,
    PageBlock,
    Post,
)
from files.models import MediaFile
from journals.models import Publisher
from portal.models import AuditLog, PublisherUser

User = get_user_model()


def make_user(username):
    return User.objects.create_user(username=username, password="x")


def make_publisher(name):
    return Publisher.objects.create(name=name)


def truncate_in_scope():
    """Delete every row in cms, portal, and files models."""
    AuditLog.objects.all().delete()
    PublisherUser.objects.all().delete()
    PageBlock.objects.all().delete()
    MembersHeaderBlock.objects.all().delete()
    BlockPage.objects.all().delete()
    MenuItem.objects.all().delete()
    HeaderSettings.objects.all().delete()
    Post.objects.all().delete()
    Page.objects.all().delete()
    Category.objects.all().delete()
    MediaFile.objects.all().delete()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="astrometrics-test-"))
class ExportImportRoundTripTests(TestCase):
    """End-to-end round trip with explicit assertions on key invariants."""

    @classmethod
    def setUpTestData(cls):
        cls.creator = make_user("alice")
        cls.publisher = make_publisher("Acme Press")

    def build_fixtures(self):
        """Create one representative row per important model.

        Migrations seed some singleton rows (e.g. HeaderSettings); clear those
        first so explicit creates don't collide on PK.
        """
        truncate_in_scope()
        category = Category.objects.create(name="News", slug="news")

        page = Page.objects.create(
            title="About Us",
            slug="about",
            body="<p>hello</p>",
            is_published=True,
        )

        post = Post.objects.create(
            title="Hello World",
            slug="hello-world",
            body="<p>post body</p>",
            is_published=True,
        )
        post.categories.add(category)

        media = MediaFile.objects.create(
            id=uuid.uuid4(),
            display_name="Sample",
            slug="sample",
            extension="txt",
            file=SimpleUploadedFile(
                "sample.txt", b"hello bytes", content_type="text/plain"
            ),
            original_filename="sample.txt",
            mime_type="text/plain",
            size=11,
            created_by=self.creator,
        )

        header = HeaderSettings.objects.create()
        parent_item = MenuItem.objects.create(
            header=header, label="Top", url="/top", sort_order=0
        )
        MenuItem.objects.create(
            header=header,
            label="Child",
            url="/top/child",
            parent=parent_item,
            sort_order=1,
        )

        block_page = BlockPage.objects.create(name="Members", slug="members")
        block = MembersHeaderBlock.objects.create(heading="Our members.")
        page_block = PageBlock.objects.create(
            content_type=ContentType.objects.get_for_model(BlockPage),
            page_id=block_page.pk,
            block_type=block.BLOCK_TYPE,
            object_id=block.pk,
            sort_order=0,
        )

        portal_user = User.objects.create_user(username="bob", password="x")
        publisher_user = PublisherUser.objects.create(
            user=portal_user, publisher=self.publisher
        )

        audit = AuditLog.objects.create(
            user=self.creator,
            content_type=ContentType.objects.get_for_model(Page),
            object_id=page.pk,
            object_repr=str(page),
            action=AuditLog.ACTION_UPDATE,
            field="title",
            old_value="old",
            new_value="new",
        )

        return {
            "category": category,
            "page": page,
            "post": post,
            "media": media,
            "header": header,
            "parent_item": parent_item,
            "block_page": block_page,
            "block": block,
            "page_block": page_block,
            "portal_user": portal_user,
            "publisher_user": publisher_user,
            "audit": audit,
        }

    def test_round_trip_preserves_in_scope_data(self):
        original = self.build_fixtures()
        original_pks = {
            name: obj.pk
            for name, obj in original.items()
            if hasattr(obj, "pk")
        }
        media_path = original["media"].file.name
        media_bytes = default_storage.open(media_path, "rb").read()

        # Export.
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            archive_path = tmp.name
        call_command("export_content", archive_path, stdout=io.StringIO())

        # Wipe in-scope tables and remove the media file from disk so the
        # restore step has to actually put it back.
        truncate_in_scope()
        if default_storage.exists(media_path):
            default_storage.delete(media_path)

        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(MediaFile.objects.count(), 0)

        # Import.
        call_command(
            "import_content",
            archive_path,
            "--default-user",
            "alice",
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

        # Scalar + PK preservation.
        page = Page.objects.get(pk=original_pks["page"])
        self.assertEqual(page.slug, "about")
        self.assertTrue(page.is_published)

        # M2M relationship preserved.
        post = Post.objects.get(pk=original_pks["post"])
        self.assertEqual(
            list(post.categories.values_list("slug", flat=True)),
            ["news"],
        )

        # External User FK resolved by username.
        media = MediaFile.objects.get(pk=original_pks["media"])
        self.assertEqual(media.created_by.username, "alice")

        # Media file restored with original bytes.
        self.assertTrue(default_storage.exists(media_path))
        self.assertEqual(
            default_storage.open(media_path, "rb").read(), media_bytes
        )

        # Self-referential FK (MenuItem.parent) restored.
        child = MenuItem.objects.get(label="Child")
        self.assertEqual(child.parent.label, "Top")

        # GenericForeignKey on PageBlock — content_type and object_id resolve.
        page_block = PageBlock.objects.get(pk=original_pks["page_block"])
        self.assertEqual(
            page_block.content_type,
            ContentType.objects.get_for_model(BlockPage),
        )
        self.assertEqual(page_block.page_id, original_pks["block_page"])
        self.assertEqual(page_block.object_id, original_pks["block"])

        # External Publisher FK resolved by name.
        pu = PublisherUser.objects.get(pk=original_pks["publisher_user"])
        self.assertEqual(pu.publisher.name, "Acme Press")
        self.assertEqual(pu.user.username, "bob")

        # AuditLog ContentType FK resolved.
        audit = AuditLog.objects.get(pk=original_pks["audit"])
        self.assertEqual(
            audit.content_type, ContentType.objects.get_for_model(Page)
        )
        self.assertEqual(audit.object_id, page.pk)

        # PK sequence reset: a new Page should not collide with imported PKs.
        new_page = Page.objects.create(title="Fresh", slug="fresh")
        self.assertGreater(new_page.pk, page.pk)

    def test_skips_publisher_user_when_publisher_missing(self):
        """When journals.Publisher.name doesn't exist on target, skip the row."""
        portal_user = User.objects.create_user(username="carol", password="x")
        ghost_publisher = make_publisher("Ghost Press")
        PublisherUser.objects.create(
            user=portal_user, publisher=ghost_publisher
        )

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            archive_path = tmp.name
        call_command("export_content", archive_path, stdout=io.StringIO())

        truncate_in_scope()
        ghost_publisher.delete()

        call_command(
            "import_content",
            archive_path,
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

        # The PublisherUser referencing the missing publisher should be gone;
        # the user account itself is untouched (it's external).
        self.assertFalse(
            PublisherUser.objects.filter(user__username="carol").exists()
        )
        self.assertTrue(User.objects.filter(username="carol").exists())

    def test_default_user_used_when_user_missing(self):
        """A nullable created_by FK falls back to --default-user."""
        ghost_user = make_user("ghost")
        MediaFile.objects.create(
            id=uuid.uuid4(),
            display_name="ghost-owned",
            slug="ghost-owned",
            extension="txt",
            file=SimpleUploadedFile("g.txt", b"x"),
            original_filename="g.txt",
            created_by=ghost_user,
        )

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            archive_path = tmp.name
        call_command("export_content", archive_path, stdout=io.StringIO())

        MediaFile.objects.all().delete()
        ghost_user.delete()

        call_command(
            "import_content",
            archive_path,
            "--default-user",
            "alice",
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

        media = MediaFile.objects.get(slug="ghost-owned")
        self.assertEqual(media.created_by.username, "alice")
