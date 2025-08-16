FROM php:8.2-apache

# extensões PHP que você usa
RUN docker-php-ext-install mysqli

# instalar ping e permissões
RUN apt-get update \
 && apt-get install -y --no-install-recommends iputils-ping libcap2-bin \
 && setcap cap_net_raw+ep /bin/ping \
 && rm -rf /var/lib/apt/lists/*

# habilitar rewrite e ServerName (se ainda não fez)
RUN a2enmod rewrite \
 && echo "ServerName localhost" > /etc/apache2/conf-available/servername.conf \
 && a2enconf servername \
 && printf '<Directory /var/www/html>\n  AllowOverride All\n  Require all granted\n</Directory>\n' \
    > /etc/apache2/conf-available/allowoverride.conf \
 && a2enconf allowoverride

WORKDIR /var/www/html
COPY ./src/ /var/www/html/

RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html
