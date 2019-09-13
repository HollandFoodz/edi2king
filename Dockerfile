FROM python:2.7.16-alpine

# Install dependencies
# For Django template error: https://stackoverflow.com/questions/8996549/admin-site-templatedoesnotexist-at-admin
RUN pip install --no-binary Django django==1.4.13 cherrypy==3.2.2 Genshi==0.7


# Install bots
RUN wget -O bots-3.2.0.tar.gz https://sourceforge.net/projects/bots/files/bots%20open%20source%20edi%20software/3.2.0/bots-3.2.0.tar.gz/download \
    && tar -xf bots-3.2.0.tar.gz \
    && cd bots-3.2.0 \
    && python setup.py install


# Create non-root user and set rights
RUN addgroup -S bots && adduser -S bots -G bots
# RUN chown -R bots /usr/local/lib/python2.7/site-packages/bots

# Set volume paths and create symlink
RUN ln -s /usr/local/lib/python2.7/site-packages/bots /app

ENV bots_installation_path=/usr/local/lib/python2.7/site-packages/bots

# Start up bots-webserver:
# USER bots
CMD bots-webserver.py