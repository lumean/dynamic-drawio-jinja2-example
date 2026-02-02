/* https://github.com/tuunit/mkdocs-drawio

This script fixes drawio not loading with the mkdocs material instant-loading (navigation.instant)
*/
document$.subscribe(({ body }) => {
  // documentation https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/diagramly/GraphViewer.js
  GraphViewer.prototype.minWidth = 500;
  GraphViewer.processElements();
  // required to fix duplicate display of external drawio graphs
  reload();
})