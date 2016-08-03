#!/usr/bin/env python
import os
import sys


def main():
    profile = os.environ.setdefault("movie_crawler_PROFILE", "dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_crawler.settings.%s" % profile)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
