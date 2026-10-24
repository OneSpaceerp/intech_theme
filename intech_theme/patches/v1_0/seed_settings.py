"""Give a site that installed an earlier build every setting this release added."""

from intech_theme.install import apply_branding, seed_settings


def execute():
	seed_settings()
	apply_branding()
