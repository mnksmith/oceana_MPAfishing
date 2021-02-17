import fiona
from unidecode import unidecode

with fiona.open('/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp', 'r') as source:

    # Create an output shapefile with the same schema,
    # coordinate systems. ISO-8859-1 encoding.
    with fiona.open(
            'natura2000_transliterated.shp', 'w',
            **source.meta) as sink:

        # Identify all the str type properties.
        str_prop_keys = [
            k for k, v in sink.schema['properties'].items()
                if v.startswith('str')]

        for rec in source:

            # Transliterate and update each of the str properties.
            for key in str_prop_keys:
                val = rec['properties'][key]
                if val:
                    rec['properties'][key] = unidecode(val)

            # Write out the transformed record.
            sink.write(rec)