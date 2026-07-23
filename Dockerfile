FROM ghcr.io/eol-uchile/edx-platform:testing-eol-lilac AS base
# Install private requirements: this is useful for installing custom xblocks.
# In particular, to install xblocks from a private repository, clone the
# repositories to ./requirements on the host and add `-e ./myxblock/` to
# ./requirements/xblocks.txt.
COPY ./requirements/ /openedx/requirements
RUN pip install --src ../venv/src -r /openedx/requirements/python_packages.txt
RUN pip install --src ../venv/src -r /openedx/requirements/apps.txt
RUN pip install --src ../venv/src -r /openedx/requirements/apis.txt
RUN pip install --src ../venv/src -r /openedx/requirements/reports.txt
RUN pip install --src ../venv/src -r /openedx/requirements/xblocks.txt
RUN pip install --src ../venv/src -r /openedx/requirements/tabs_plugins.txt

# Copy themes
COPY ./themes/ /openedx/themes/

# Copy settings with added COMPREHENSIVE_THEME_LOCALE_PATHS for themes
COPY ./lms-assets.py /openedx/edx-platform/lms/envs/prod/assets.py
COPY ./cms-assets.py /openedx/edx-platform/cms/envs/prod/assets.py

# staticfiles env
ENV STATIC_ROOT_LMS=/openedx/staticfiles/
ENV STATIC_ROOT_CMS=/openedx/staticfiles/studio/

# Build static assets
RUN openedx-assets xmodule
RUN openedx-assets npm
RUN openedx-assets webpack --env=prod
RUN openedx-assets common
RUN openedx-assets themes
RUN python manage.py lms --settings=prod.assets compilejsi18n
RUN python manage.py cms --settings=prod.assets compilejsi18n
RUN openedx-assets collect --settings=prod.assets

# production settings
ENV SETTINGS=prod.production

FROM rclone/rclone:1.56.0 AS s3

COPY --from=base /openedx/staticfiles /data
