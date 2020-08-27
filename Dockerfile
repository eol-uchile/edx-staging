FROM eoluchile/edx-platform:eede1121158a253ce84d192d4d4861b6adeb3baf

# Install private requirements: this is useful for installing custom xblocks.
# In particular, to install xblocks from a private repository, clone the
# repositories to ./requirements on the host and add `-e ./myxblock/` to
# ./requirements/private.txt.
COPY ./requirements/ /openedx/requirements
RUN touch /openedx/requirements/private.txt \
    && pip install --src ../venv/src -r /openedx/requirements/private.txt

# Copy themes
COPY ./themes/ /openedx/themes/
RUN openedx-assets themes \
    && openedx-assets collect --settings=prod.assets
