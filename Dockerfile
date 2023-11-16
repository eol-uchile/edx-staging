FROM ghcr.io/eol-uchile/edx-platform:testing-koa as base
# Install private requirements: this is useful for installing custom xblocks.
# In particular, to install xblocks from a private repository, clone the
# repositories to ./requirements on the host and add `-e ./myxblock/` to
# ./requirements/private.txt.
COPY ./requirements/ /openedx/requirements
RUN /openedx/requirements/python_packages.txt \
    && pip install --src ../venv/src -r /openedx/requirements/python_packages.txt
RUN /openedx/requirements/apps.txt \
    && pip install --src ../venv/src -r /openedx/requirements/apps.txt
RUN /openedx/requirements/apis.txt \
    && pip install --src ../venv/src -r /openedx/requirements/apis.txt
RUN /openedx/requirements/reports.txt \
    && pip install --src ../venv/src -r /openedx/requirements/reports.txt
RUN /openedx/requirements/xblocks.txt \
    && pip install --src ../venv/src -r /openedx/requirements/xblocks.txt
RUN /openedx/requirements/tabs_plugins.txt \
    && pip install --src ../venv/src -r /openedx/requirements/tabs_plugins.txt

# Copy themes
COPY ./themes/ /openedx/themes/

# Build static assets
RUN openedx-assets themes \
    # Rebuild translations
    && python manage.py lms --settings=prod.assets compilejsi18n \
    && python manage.py cms --settings=prod.assets compilejsi18n \
    && openedx-assets collect --settings=prod.assets

FROM rclone/rclone:1.53 as s3

COPY --from=base /openedx/staticfiles /data
