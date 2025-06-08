import csv
import decimal as dec


class CSVManager(list):
    def __init__(self, csv_name, figures=1):
        super().__init__(self)

        self.csv_name = csv_name
        self.figures = figures

        with open(csv_name, 'r') as csv_file:
            for row in csv.DictReader(csv_file):

                read = dict()
                for key, val in row.items():
                    read[key] = dec.Decimal(val)

                self.append(read)

    def __error_fmt__(self, value, error):
        shift_places = - error.adjusted() - 1 + self.figures
        shift = dec.Decimal(10) ** shift_places

        error = error * shift
        error = error.to_integral_value()

        value = value.quantize(error/shift)

        return value, error

    def keyerror(self, key, error_calc, *args, **kwargs):
        for row in self:
            row[key + 'err'] = error_calc(row, *args, **kwargs)

    def rowapply(self, operation, *args, **kwargs):
        for row in self:
            row = operation(row, *args, **kwargs)

    def rowfilter(self, test, *args, **kwargs):
        to_remove = list()

        for i in range(len(self)):
            if test(self[i], *args, **kwargs):
                to_remove.append(i)

        for j in range(len(to_remove)):
            del self[to_remove[j]-j]

    def close(self):
        for key in self[0].keys():
            if key + 'err' in self[0].keys():
                for row in self:
                    val, err = self.__error_fmt__(row[key], row[key + 'err'])
                    row[key], row[key + 'err'] = val, err

        with open(self.csv_name, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, self[0].keys())
            writer.writeheader()
            writer.writerows(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


##################
# Data functions #
##################

def setup_names(row, changes):
    for old, new in changes:
        if old in row.keys():
            row[new] = row[old]
            del row[old]
    return row


def remove_fields(row, fields):
    for field in fields:
        if field in row.keys():
            del row[field]


###################
# Error functions #
###################

def V_error(row, channel, vertical_position=0, div=1):
    key = 'V' + str(channel)

    # 3% of adjusted value
    err_percent = dec.Decimal('0.3') / dec.Decimal(100)
    # ajusted values: V + position
    V_adj = row[key] + dec.Decimal(vertical_position)
    # scale division error
    div_err = dec.Decimal('.2') * dec.Decimal(div) / dec.Decimal(1000)
    # fixed error
    fix_err = dec.Decimal(7) / dec.Decimal(1000)

    return err_percent * V_adj + div_err + fix_err


def T_error(row, input_channel, output_channel):
    V_in = 'V' + str(input_channel)
    V_out = 'V' + str(output_channel)

    # error as: 20/ln(10) * sqrt of SUM[i,o](Verr/V)
    # derived from: T (in dB) = 20 log10(Vo/Vi)
    errs = [row[V+'err']/row[V] for V in (V_in, V_out)]
    err = sum([err**2 for err in errs]).sqrt()
    err_adj = dec.Decimal(20)/dec.Decimal(10).ln()

    return err_adj * err


def freq_error(row, ppm=100):
    row['freq']

    err_ppm = dec.Decimal(ppm)/dec.Decimal('10')**6   # 100 ppm
    fix_err = dec.Decimal(1) * dec.Decimal('10')**-6  # 1 uHz

    return row['freq'] * err_ppm + fix_err


######################
# Managing data file #
######################
files = [
    "dados/transmitancias_RC.csv",
    "dados/transmitancias_RLC.csv"
]
new_names = [
    ('frequencia', 'freq'),
    ('Terr', 'TdBerr'),
    ('T_dB', 'TdB'),
    ('Vpp1', 'V1'),
    ('Vpp2', 'V2')
]
fields = ['fase', 'T']

for file in files:
    with CSVManager(file) as amostra:
        amostra.rowapply(setup_names, new_names)
        amostra.rowapply(remove_fields, fields)

        amostra.keyerror('V1', V_error, 1)
        amostra.keyerror('V2', V_error, 2)
        amostra.keyerror('TdB', T_error, 1, 2)
        amostra.keyerror('freq', freq_error)
