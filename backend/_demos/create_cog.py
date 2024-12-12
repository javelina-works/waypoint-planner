from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles


def convert_geotiff_cog(input_tif, output_path="output_cog.tif"):

    # Select a profile, for example "deflate"
    # Available profiles: "jpeg", "webp", "lzw", "deflate", "packbits", ...
    profile = cog_profiles.get("deflate")

    cog_translate(
        input_tif,
        output_path,
        profile,
        in_memory=False,
        web_optimized=True,
        # You can adjust block size and overviews as needed:
        # blocksize=512, 
        # overview_level=6,
        # add_mask=True,
    )
    print("COG created:", output_path)


input_image = "input/ESPG-4326-orthophoto.tif"
convert_geotiff_cog(input_image)