"""Jinja helpers for the templates this app overrides."""

from intech_theme.branding import get_brand_name, get_settings


def intech_settings():
	return get_settings()


def intech_brand_name():
	return get_brand_name()
