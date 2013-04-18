DEBUG = True

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dbname',
    'HOST': 'hostname.amazonaws.com',
    'PORT': 5432,
    'USER': 'dbuser',
    'PASSWORD': 'dbpass'
  }
}
