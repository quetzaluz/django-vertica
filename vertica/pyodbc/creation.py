from django.db.backends.creation import BaseDatabaseCreation
import base64
from django.utils.hashcompat import md5_constructor
import random

class DataTypesWrapper(dict):
    def __getitem__(self, item):
        if item in ('PositiveIntegerField', 'PositiveSmallIntegerField'):
            # The check name must be unique for the database. Add a random
            # component so the regresion tests don't complain about duplicate names
            fldtype = {'PositiveIntegerField': 'int', 'PositiveSmallIntegerField': 'smallint'}[item]
            rnd_hash = md5_constructor(str(random.random())).hexdigest()
            unique = base64.b64encode(rnd_hash, '__')[:6]
            return '%(fldtype)s CONSTRAINT [CK_%(fldtype)s_pos_%(unique)s_%%(column)s] CHECK ([%%(column)s] >= 0)' % locals()
        return super(DataTypesWrapper, self).__getitem__(item)

class DatabaseCreation(BaseDatabaseCreation):
    # This dictionary maps Field objects to their associated Vertica SQL column
    # types, as strings. Column-type strings can contain format strings; they'll
    # be interpolated against the values of Field.__dict__ before being output.
    # If a column type is set to None, it won't be included in the output.
    #
    # Any format strings starting with "qn_" are quoted before being used in the
    # output (the "qn_" prefix is stripped before the lookup is performed.

#    data_types = DataTypesWrapper({
    data_types = {
        'AutoField':         'IDENTITY (1, 1)',
        'BooleanField':      'BOOLEAN',
        'CharField':         'VARCHAR(%(max_length)s)',
        'CommaSeparatedIntegerField': 'VARCHAR(%(max_length)s)',
        'DateField':         'DATE',
        'DateTimeField':     'DATETIME',
#        'DecimalField':      'numeric(%(max_digits)s, %(decimal_places)s)',
        'DecimalField':      'DECIMAL',
        'FileField':         'VARCHAR(%(max_length)s)',
        'FilePathField':     'VARCHAR(%(max_length)s)',
        'FloatField':        'FLOAT',
        'IntegerField':      'INTEGER',
        'IPAddressField':    'VARCHAR(15)',
        'NullBooleanField':  'BOOLEAN',
        'OneToOneField':     'INTEGER',
        #'PositiveIntegerField': 'integer CONSTRAINT [CK_int_pos_%(column)s] CHECK ([%(column)s] >= 0)',
        #'PositiveSmallIntegerField': 'smallint CONSTRAINT [CK_smallint_pos_%(column)s] CHECK ([%(column)s] >= 0)',
        'PositiveIntegerField': 'INTEGER',
        'PositiveSmallIntegerField': 'SMALLINT',
        'SlugField':         'VARCHAR(%(max_length)s)',
        'SmallIntegerField': 'SMALLINT',
        'TextField':         'VARCHAR(65000)',
        'TimeField':         'TIME',
    }
    #})

    def _destroy_test_db(self, test_database_name, verbosity):
        "Internal implementation - remove the test db tables."
        cursor = self.connection.cursor()
        self.set_autocommit()
        #time.sleep(1) # To avoid "database is being accessed by other users" errors.
        cursor.execute("ALTER DATABASE %s SET SINGLE_USER WITH ROLLBACK IMMEDIATE " % \
                self.connection.ops.quote_name(test_database_name))
        cursor.execute("DROP DATABASE %s" % \
                self.connection.ops.quote_name(test_database_name))
        self.connection.close()
