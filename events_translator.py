import argparse
import re
import pandas as pd

agents_id = pd.read_csv("agents_id.csv")

def get_type_from_id(id):
    return agents_id[agents_id["id"]==id]["tipo"].values[0]

def create_verbose_csv(filename):
    m = re.search('\d', text)
    type_event = m.group(1) if m else -1
    events = pd.read_csv(filename)
    newdf=[]
    if type_event == 1:
        for row in events.itertuples(index=True, name='Pandas'):
            newdf.append((row.timestamp, f"{get_type_from_id(row.X)} {row.X}", f"{get_type_from_id(row.Y)} {row.Y}", f"{get_type_from_id(row.Z)} {row.Z}"))
        df = pd.DataFrame(newdf, columns=["timestamp", "X", "Y", "Z"])
    elif type_event == 2:
        for row in events.itertuples(index=True, name='Pandas'):
            newdf.append((row.timestamp, f"{get_type_from_id(row.A)} {row.A}", f"{get_type_from_id(row.X)} {row.X}", f"{get_type_from_id(row.Y)} {row.Y}"))
        df = pd.DataFrame(newdf, columns=["timestamp", "A", "X", "Y"])
    elif type_event == 3:
        for row in events.itertuples(index=True, name='Pandas'):
            newdf.append((row.timestamp, f"{get_type_from_id(row.X)} {row.X}", f"{get_type_from_id(row.Y)} {row.Y}",
                         f"{get_type_from_id(row.A)} {row.A}", f"{get_type_from_id(row.Z)} {row.Z}"))
        df = pd.DataFrame(newdf, columns=["timestamp", "X", "Y", "A", "Z"])

    elif type_event == 4:
        for row in events.itertuples(index=True, name='Pandas'):
            newdf.append((row.timestamp, f"{get_type_from_id(row.A)} {row.A}", f"{get_type_from_id(row.X)} {row.X}",
                         f"{get_type_from_id(row.B)} {row.B}", f"{get_type_from_id(row.Y)} {row.Y}"))
            df = pd.DataFrame(newdf, columns=["timestamp", "A", "X", "B", "Y"])

    else:
        for row in events.itertuples(index=True, name='Pandas'):
            newdf.append((row.timestamp, f"{get_type_from_id(row.u1)} {row.u1}", f"{get_type_from_id(row.u2)} {row.u2}",
                          f"{get_type_from_id(row.u3)} {row.u3}", f"{get_type_from_id(row.u4)} {row.u4}"))
            df = pd.DataFrame(newdf, columns=["timestamp", "u1", "u2", "u3", "u4"])

    df.to_csv("output.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('filename', type=str, help='Nome del file di eventi')

    args = parser.parse_args()
    if not args.filename:
        print("Manca il filename")
    else:
        create_verbose_csv(args.filename)