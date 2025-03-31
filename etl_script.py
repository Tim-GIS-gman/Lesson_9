
import arcpy
import requests
import csv
import os

def extract(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during extract: {e}")
        return None

def transform(data):
    if not data:
        print("No data to transform.")
        return []

    transformed = []
    for record in data:
        if 'name' in record and 'longitude' in record and 'latitude' in record:
            transformed.append({
                'name': record['name'].strip(),
                'longitude': float(record['longitude']),
                'latitude': float(record['latitude'])
            })

    return transformed

def write_to_csv(data, csv_path):
    fieldnames = ['name', 'longitude', 'latitude']
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def load(input_table, output_fc, x_field="longitude", y_field="latitude", spatial_reference=4326):
    try:
        arcpy.management.XYTableToPoint(
            in_table=input_table,
            out_feature_class=output_fc,
            x_field=x_field,
            y_field=y_field,
            coordinate_system=arcpy.SpatialReference(spatial_reference)
        )
        print(f"Loaded data into: {output_fc}")
    except arcpy.ExecuteError:
        print(f"ArcPy error: {arcpy.GetMessages(2)}")
    except Exception as e:
        print(f"General error in load: {e}")

def main():
    url = "https://example.com/api/data"  # Replace with actual data source
    raw_data = extract(url)
    transformed_data = transform(raw_data)

    if transformed_data:
        csv_path = r"C:\GIS\data\clean_data.csv"
        gdb_path = r"C:\GIS\output.gdb\extracted_points"

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        write_to_csv(transformed_data, csv_path)

        load(csv_path, gdb_path)

if __name__ == "__main__":
    main()


