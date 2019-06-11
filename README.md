# directx-exporter
Exporter from Blender to DirectX - adapted from [Ben Omari's version](http://xoomer.virgilio.it/glabro1/index.html).

I was doing my development using Blender 2.45, so I make no promises that it will still work with earlier versions.

## New features include: (updated 17th April 2009):

  * Improved error handling and plenty of warning messages to help you work out why the .X file it’s spewing out is a load of gibberish that won’t open in your DirectX application
  * Added new templates to support Shape Keys (morph targets). Obviously you’ll need to write some code on the DirectX side to actually make use of this data – feel free to email me for some ideas on this
  * It now correctly reverses the winding order when an object has a negative scaling factor
  * Many more bug fixes and improvements

It comes with the following caveats and warnings:

  * I believe the “Export Selected” button to be somewhat buggy. My advice is to stick to the “Export All” button.
  * The “Dedup” button I added to write out a VertexDuplicationIndices template doesn’t seem to work. I get a stupid error message “Invalid DuplicationIndices in x file. All duplicates must refer to the same vertex index”.
  
This code is provided "as is" and I have long since stopped doing any work which involves using it, so I have not touched the code (or Blender) in a LONG time.
