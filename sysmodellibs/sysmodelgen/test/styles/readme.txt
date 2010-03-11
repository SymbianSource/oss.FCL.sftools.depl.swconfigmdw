Tests:
This tests styles in the Shapes XML file
- specifying CSS: layers are filled in with colour #90f090 and have a red border
- dashed borders: "fake" components have dashed borders
- styling collections: java collections have thick dashed borders
- backwards compatibility: <style match="module"> works the same as <style match="collection">
- border highlighting: borders have back or orange glow outside of borders. 
- text highlighting on collections: Any collection with four components will have the label outlined in blue
- mixing rules and values for colours: colours based on OSD are values, the rest are rules
- Item background colours: some collections, blocks and subblocks have background colours

Differences:

ini-output.svg has CoreOS colouring. Turning off the colouring turns on the alignment of the top two layers.

The order of the legend is different between ini-output.svg and model-output.svg. When using an ini file the legend order is arbitrary, while it can be controlled in the model.xml.


