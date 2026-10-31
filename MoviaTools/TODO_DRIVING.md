# Huskeliste – Driving-skærmen

**STATUS 24/10 kl. ~09.45: punkt 1–6 er lavet og bygget – mangler test i spillet.**
- 3: Planlagt ankomst er korrekt (04:58 = køreplanens ankomst). Navigatorens 05:00 er sandsynligvis spillets FORVENTEDE ankomst (rød = du når det ikke til tiden ved nuværende fart). Nyt felt `NaesteAfgang` findes, hvis afgangstid ønskes.

# (gammel liste) (fra brugerens test 24/10 07:09, IKKE lavet endnu)
1. Tekst overlapper/grim:
   - Langt stopnavn (Hebebrandstraße) løber ind i "Planlagt ankomst"-tiden -> mindre skrift/klip/bredere boks.
   - Destination i headeren er sort tekst på sort baggrund (skal være hvid / spillets gamle tekst skjules).
   - Stort ur (HH:MM:SS) bliver skåret af menu-knappen -> ryk til venstre / mindre.
   - Skrifttype/placering ser off ud generelt; labels sidder skævt.
2. Label "Forsinkelse:" står selv når man er for tidlig (grøn, -1:21) -> skift label efter fortegn (fx "Før tid:" når Forsinkelse < 0).
3. Planlagt ankomst viser 04:58:00, men spillets navigator viser Arrival 05:00 -> find hvilket felt spillet bruger (DepartureTime? afrunding?) og brug samme.
4. Næste stop skifter for tidligt: når man holder ved stoppet (Arrival -> Departure) viser systemet stoppet efter.
   Skal blive ved det aktuelle stop indtil bussen kører fra stoppet (GetCurrentStop mens man holder der, ikke GetCurrentOrNextStop/offset).
5. Linje-boksen ("218") skal se pænere ud: teksten er grå/udvasket og bleg på lyseblå, ikke centreret pænt.
   -> klar hvid fed skrift, centreret, rigtig Movia-blå baggrund, evt. lidt større boks/padding.
6. Rigtigt GPS-kort i stedet for det faste baggrundsbillede (Kort, z -20):
   - Skal virke som spillets egen navigator (den lille i hjørnet: rute, pil, afstand, Arrival/Departure, fartgrænse),
     men med et custom Movia-tema (farver på veje/rute/baggrund).
   - Undersøg: kan spillets navigator-widget/render target (minimap) genbruges og farves om, eller skal kortet tegnes selv
     ud fra bussens position + rutens stop (RouteStopInfo.WorldPosition).
   - Stil: lidt 3D-vibe (skrå/perspektiv-visning som en rigtig bil-GPS), med en 3D-cirkel/ring rundt om BUSSTOPPET (næste stop på kortet) – IKKE om bussen.

## Research notes (24/10, only read, nothing built)
- Item 3 (04:58 vs 05:00): RouteStopWithTime has BOTH arrival_time and departure_time, and RouteStopInfo has
  waiting_time. The navigator almost certainly shows departure_time (arrival + waiting time). -> Show DepartureTime
  (or both) and check against the navigator.
- Item 4 (stop switches on arrival): BusTripInfo has current_stop_index plus functions get_current_stop,
  get_previous_or_current_stop, get_next_stop. Use get_previous_or_current_stop while the bus is at the stop
  (doors open / speed ~0 near the stop) and only switch once it has left (distance grows / departure).
- Item 6 GPS: the game has its own plugin "RoadmapSystem" with:
  * MapRenderWidget  = a UMG widget that draws the road map itself (this is probably what the navigator uses) -> can be
    placed directly in our Driving screen instead of the Kort image.
  * RoadMapSettings: road_render_settings, navi_settings, road_icon_settings, map_icon_size, min/max_zoom_factor,
    spline_thickness_scale, text_font, text_outline_color, player_excluded_roads_color -> this is where the colour theme is set.
  * DefaultEngine.ini has AllowRoadmap3DRendering=1 -> the map supports 3D/tilted view (the 3D vibe).
  * RoadMapManager: get_path / get_path_color(_as_hex) / add_path / get_roads_in_bounds / add_dynamic_map_element
    (fx vores egen 3D-ring om næste BUSSTOP som kort-element – IKKE om bussen).
  * LineRoute: waypoints, path, path_bounds, compute_path_zoom (zoom the map onto the route).
  Next time: probe MapRenderWidget's properties/functions in Python (dir()), find the navigator widget in
  the game (UMG for the little navigator in the corner) and copy/restyle it.

## 24/10 kl. 10.30 – Passagerskærm: linje-mærker + afgangstavle (bygget, ikke testet)
- Under hvert af de 3 stop: op til 5 mærker med andre linjer (gul / blå for S-busser) – hentes fra spillets afgangstavle-system (BusStopDisplay) for det stop.
- Ved stoppet (holder der / < 40 m): afgangstavle "Bus" med Linje / Til / Om min. (7 rækker), som billedet. Metro-kolonnen er udeladt (spillet har ingen metro-data) – bus-tabellen fylder hele bredden.
- Dørene: spillet giver ikke dør-status nemt; "ved stoppet" bruges i stedet.
