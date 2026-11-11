# Follow the wood: maps for the Conversation sequel

Two maps for "Cutting a tree can help save a forest, but only if the wood has somewhere to go" (The Conversation, draft, November 2026).

* `2026-11-06_follow-the-wood-maps_DRAFT.R` builds both maps in R with ggplot2, maps, mapdata and ggrepel.
* `2026-11-06_follow-the-wood-map_DRAFT.png`: schematic routes (Saint John to Macon, Brazil to U.S. buyers) and Maine's 2023 outbound and inbound wood.
* `2026-11-06_maine-mill-towns-map_DRAFT.png`: Jay, Madison, Lincoln, Saco and Orono.

Routes are schematic and show origin and destination, not shipping paths. Figures cited on the maps come from J.D. Irving, Rabobank, the Maine Forest Service 2023 Wood Processor Report (via maineforestdashboard.com), Maine TREE Foundation, Boston Globe, Mainebiz, UMaine News, Maine Public and the UMaine Process Development Center.

Graphic: Center for Research on Sustainable Forests, University of Maine.

Note (November 10, 2026): the Millinocket and Ashland (WholeTrees) markers and labels on the mill towns map were added to the PNG by hand after the R run, and the Millinocket label was shifted left to clear the Ashland marker; the R script does not yet draw them.

Note (November 10, 2026): the follow the wood map was rerun in R with label collisions cleared and the Brazil route ending on the U.S. coast. `2024_maine-wood-exports-world-map_DATA.png` is the Maine Forest Dashboard's world export map (U.S. Census Bureau, USA Trade Online, 2024), copied here for use in the article with white side margins added to fit the figure slot.

Note (November 10, 2026): `2026-11-10_follow-the-wood-leakage-map_DRAFT.png` and its R script put the article's routes over a carbon leakage layer. The layer (`2025_daigneault-erl-fig2a-leakage-layer_DATA.png`, with its legend bar) is cropped from figure 2a of Daigneault, Sohngen, Belair and Ellis (2025), Environmental Research Letters 20:114022, https://doi.org/10.1088/1748-9326/ae0ce2, used under CC BY 4.0, and georeferenced by fitting coastline extremes. It shows mean carbon leakage for extended rotations at a 10% implementation rate. It is an image of the published figure, not the underlying data.

Note (November 10, 2026): files ending in `-nofooter` are the same figures with the source and credit lines cropped off the bottom for the article, where sources and credits are carried in the captions instead.

Note (November 10, 2026): `2026-11-10_maine-mill-towns-quebec-mills-map_DRAFT.png` replaces the mill towns map in the article. It shows seven Maine towns that lost a paper mill since 2008 (Bangor Daily News, September 26, 2019; Boston Globe for Jay; Old Town's 2023 closure), new uses in Madison, Ashland and Saco, and the Quebec wood mills within 50 km of the Maine border. The Quebec points come from the Gouvernement du Quebec list of permitted primary wood processing mills (CC BY 4.0, file updated June 25, 2026); the 46 mills within 50 km are in `2026-06-25_quebec-mills-within-50km-of-maine_DATA.csv`. Distance is measured to the Maine outline in the R maps package, so it is approximate. New Brunswick mills are not mapped. The image carries no footer; sources are in the article caption.

Note (November 10, 2026, later): the mill map now has a forest layer and the Nackawic, New Brunswick, pulp mill, which its owner idled in October 2026 (CTV News, September 17, 2026). The forest layer (`2020_cec-land-cover-forest-layer_DATA.png`) holds the forest classes of the 2020 Land Cover of North America at 30 meters (Commission for Environmental Cooperation 2023, North American Land Change Monitoring System), exported from the CEC map service for the map frame (longitude -73.6 to -65.4, latitude 42.95 to 47.95). The R script reads that file as `forest_layer.png` and the Quebec list as `qc_usines.csv`.

Note (November 10, 2026, evening): the Saint John pulp mill marker and label and the "Who owns the forest" box were added to the mill map PNG by hand because the R host was offline; the R script does not yet draw them. Ownership shares: Maine 92% private (Maine Forest Service, State of the Forest 2021-2025 review draft, 2023 FIA data); Quebec 92% public province-wide (Quebec forest inventory, as cited by the Montreal Economic Institute, October 29, 2020); New Brunswick 51% Crown land (Government of New Brunswick, Our Forests Are for Everyone).
