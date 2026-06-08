# Stefanie Jackson portfolio

TODO:
- [ ] adjust masking on diptychs

This website showcases the paintings of Stefanie Jackson.

To add new images, run the img-sizer.py script to create web-ready derivatives. For example:
`py img-sizer.py -i original_photo.tif -o smaller_file.jpg -m 1200`
This will make a version of the image that is no greater than 1200px wide (or high for tall images) and no greater than 1MB in size.

The website loads 1200px or 800px width images based on scaling and internet speed.

When new files are added to the `img` folder, update the file index by running the `json-builder.py` script.
`py json-builder.py`
This script will add new entries to the `works.json` document. You can manually edit the document to identify titles and tags associated with the images. This document will be used to dynamically loaded content through js.