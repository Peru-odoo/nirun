FROM ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest

USER root

# Move nirun module into extra-addonse and install requirment
COPY . /mnt/extra-addons
RUN pip install -r /mnt/extra-addons/requirements.txt

RUN apt update \
    && apt -yq install curl

HEALTHCHECK --start-period=120s --start-interval=15s\
  CMD curl --fail http://localhost:8069/web/health || exit 1

USER odoo
