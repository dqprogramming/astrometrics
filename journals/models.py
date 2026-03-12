from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Publisher(models.Model):
    """
    Publisher organizations that publish journals.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the publisher organization",
    )
    website = models.URLField(
        blank=True, null=True, help_text="Publisher's website URL"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")

    def __str__(self):
        return self.name


class Subject(models.Model):
    """
    Academic subjects/disciplines for journals.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Subject or discipline name"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")

    def __str__(self):
        return self.name


class Language(models.Model):
    """
    Languages in which journals publish.
    """

    name = models.CharField(
        max_length=100, unique=True, help_text="Language name"
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        help_text="ISO language code (e.g., 'en', 'fr', 'es')",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return self.name


class PackageBand(models.Model):
    """
    Package band classification for journals (e.g., C1, C2, etc.).
    """

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Package band code (e.g., C1, C2)",
    )
    name = models.CharField(
        max_length=255, help_text="Descriptive name of the package band"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = _("Package Band")
        verbose_name_plural = _("Package Bands")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Journal(models.Model):
    """
    Main journal model representing academic journals.
    """

    # License choices
    LICENSE_CHOICES = [
        ("CC BY", "CC BY"),
        ("CC BY-NC", "CC BY-NC"),
        ("CC BY-NC-SA", "CC BY-NC-SA"),
        ("CC BY-NC-ND", "CC BY-NC-ND"),
        ("CC BY-SA", "CC BY-SA"),
        ("CC BY-ND", "CC BY-ND"),
    ]

    # Basic Information
    title = models.CharField(
        max_length=500, unique=True, help_text="Full journal title"
    )
    year_established = models.CharField(
        max_length=100,
        blank=True,
        help_text="Year established or original zombie designation",
    )

    # Publisher & Owner
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name="journals",
        help_text="Publishing organization",
    )
    journal_owner = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organization or entity that owns the journal",
    )

    # Cost & Package Information
    package_band = models.ForeignKey(
        PackageBand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journals",
        help_text="Package and band classification",
    )
    cost_gbp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Cost in British Pounds",
    )
    normalized_articles = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Normalized number of articles",
    )

    # URLs & Identifiers
    journal_url = models.URLField(
        blank=True, help_text="Link to journal website"
    )
    publisher_url = models.URLField(
        blank=True, help_text="Link to publisher website"
    )
    issn = models.CharField(
        max_length=20,
        blank=True,
        help_text="International Standard Serial Number",
    )

    # Content Information
    description = models.TextField(
        blank=True, help_text="Journal description and scope"
    )

    # Relationships
    languages = models.ManyToManyField(
        Language,
        related_name="journals",
        blank=True,
        help_text="Languages in which the journal publishes",
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="journals",
        blank=True,
        help_text="Academic subjects covered by the journal",
    )

    # DOAJ Status
    in_doaj = models.BooleanField(
        default=False,
        help_text=(
            "Whether journal is listed in Directory of Open Access Journals"
        ),
    )

    # Indexing
    in_scopus = models.BooleanField(
        default=False, help_text="Whether journal is indexed in Scopus"
    )
    wos_impact_factor = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Web of Science Impact Factor",
    )

    # Archive Information
    archive_available_diamond_oa = models.TextField(
        blank=True, help_text="Details about diamond OA archive availability"
    )
    archive_years = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        help_text="Number of years of archive available",
    )

    # Unique Selling Points
    usps = models.TextField(
        blank=True,
        verbose_name="USPs",
        help_text="Unique selling points to note",
    )

    # Licensing & Archiving
    licensing = models.CharField(
        max_length=100,
        choices=LICENSE_CHOICES,
        blank=True,
        help_text="Creative Commons or other license type",
    )
    archiving_services = models.TextField(
        blank=True,
        help_text="Archiving services (CLOCKSS, LOCKSS, PKP PN, etc.)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")
        indexes = [
            models.Index(fields=["publisher", "package_band"]),
            models.Index(fields=["cost_gbp"]),
            models.Index(fields=["in_doaj"]),
        ]

    def __str__(self):
        return self.title

    @property
    def cost_per_article(self):
        """Calculate cost per article if both values are available."""
        if (
            self.cost_gbp
            and self.normalized_articles
            and self.normalized_articles > 0
        ):
            return self.cost_gbp / self.normalized_articles
        return None


class ImportLog(models.Model):
    """
    Log of CSV imports for tracking and auditing purposes.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    filename = models.CharField(
        max_length=255, help_text="Name of the imported file"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Import status",
    )
    records_processed = models.IntegerField(
        default=0, help_text="Number of records processed"
    )
    records_created = models.IntegerField(
        default=0, help_text="Number of new records created"
    )
    records_updated = models.IntegerField(
        default=0, help_text="Number of existing records updated"
    )
    records_failed = models.IntegerField(
        default=0, help_text="Number of records that failed to import"
    )
    error_log = models.TextField(
        blank=True, help_text="Detailed error messages and warnings"
    )

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = _("Import Log")
        verbose_name_plural = _("Import Logs")

    def __str__(self):
        return f"{self.filename} - {self.status} ({self.started_at})"
