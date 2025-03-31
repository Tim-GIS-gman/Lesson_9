import arcpy
import requests
import csv
import os


def extract():
    """
    Downloads the CSV from a public Google Sheets link and saves it to Downloads.
    """
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDjitOlmILea7koCORJkq6QrUcwBJM7K3vy4guXB0mU_nWR6wsPn136bpH6ykoUxyYMW7wTwkzE37l/pub?output=csv"

    print("Downloading CSV...")
    r = requests.get(url)
    r.encoding = "utf-8"
    data = r.text

    output_file = r"C:\Users\madch\Downloads\addresses.csv"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"CSV saved to: {output_file}")
    return output_file


def transform(input_csv):
    """
    Reads the saved CSV and builds a cleaned address field.
    """
    transformed = []
    with open(input_csv, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                full_address = f"{row['Street Address']}, {row['Zip Code']}"
                transformed.append({
                    'Last Name': row['Last Name'],
                    'Address': full_address
                })
            except KeyError as e:
                print(f"Skipping row due to missing field: {e}")
    return transformed


def write_to_csv(data, csv_path):
    """
    Writes transformed address data to a new CSV for geocoding.
    """
    fieldnames = ['Last Name', 'Address']
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load(input_table, output_fc, locator):
    """
    Uses ArcPy to geocode addresses from CSV to a point feature class.
    """
    try:
        arcpy.geocoding.GeocodeAddresses(
            in_table=input_table,
            address_locator=locator,
            in_address_fields="Address ADDRESS",
            out_feature_class=output_fc
        )
        print(f"Geocoded addresses to: {output_fc}")
    except arcpy.ExecuteError:
        print(f"ArcPy error: {arcpy.GetMessages(2)}")
    except Exception as e:
        print(f"General error in load: {e}")


def main():
    # Extract CSV from Google Sheets
    downloaded_csv = extract()

    # Transform raw data to build full address strings
    transformed_data = transform(downloaded_csv)

    if transformed_data:
        # Prepare output paths
        transformed_csv = r"C:\GIS\data\transformed_addresses.csv"
        output_fc = r"C:\GIS\output.gdb\geocoded_pts"
        locator_path = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"

        os.makedirs(os.path.dirname(transformed_csv), exist_ok=True)

        # Create GDB if it doesn't exist
        if not arcpy.Exists(r"C:\GIS\output.gdb"):
            arcpy.management.CreateFileGDB(r"C:\GIS", "output.gdb")

        # Save transformed data and geocode
        write_to_csv(transformed_data, transformed_csv)
        load(transformed_csv, output_fc, locator_path)


if __name__ == "__main__":
    main()
