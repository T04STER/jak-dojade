# Wyniki testów porównujących wagi funkcji kary w algorytmie A*
1. Łozina - Nowego Osiedla I -> Ferma - stadnina koni @ 19:30:00
2. Biegasa -> ROD Zgoda @ 19:26:00
3. Jerzmanowska nr 9 -> Szczodre - stawy @ 21:23:00
4. Zemska -> Orlińskiego @ 10:04:00
5. Kętrzyńska -> Metalowców @ 05:45:00
6. Zajazdowa -> Zabrodzie - pętla @ 16:09:00
7. Konduktorska -> Żmudzka @ 23:14:00
8. Zgorzelisko -> Mielecka @ 23:23:00
9. Zamkowa -> Kiełczówek - skrzy. Imbirowa @ 15:03:00
10. Mikołowska -> Marszowicka @ 18:56:00
11. Damrota -> Trestno - świetlica @ 09:30:00
12. Raków - skrzy. -> Zagony @ 23:20:00
13. Bierzyce -> Libelta @ 14:15:00
14. Odrodzenia Polski -> Na Ostatnim Groszu @ 21:53:00
15. Zielińskiego -> Królewska @ 07:02:00
16. Park Tysiąclecia -> Turoszowska @ 12:48:00
17. Jerzmanowo (Cmentarz) -> Suwalska @ 08:49:00
18. Brzezia Łąka - Główna pętla -> Bierutowska 75 @ 15:12:00
19. Karwińska -> Smolec - Chłopska/Wrzosowa @ 16:27:00
20. Kamień - skrzy. Diamentowa -> Olsztyńska @ 12:39:00
21. Na Niskich Łąkach -> Opatowicka nr 85 @ 05:13:00
22. Wiaduktowa -> Śliwice @ 12:38:00
23. Krynicka -> Zajezdnia Obornicka @ 06:23:00
24. Szkocka -> Wrocław Nowy Dwór (P+R) @ 20:55:00
25. Królewiecka (Staw) -> Olbrachtowska @ 15:25:00
26. Siedlec - Wrocławska/sklep -> Wiślańska @ 22:29:00
27. Wrocław Mikołajów (Zachodnia) -> Dworska @ 18:02:00
28. Bociania -> Wilkszyn - Miłoszyn @ 06:51:00
29. Park Brochowski -> Smolec - Główna (na wys. nr 83) @ 17:03:00
30. Brzezina - Zacisze -> Częstochowska @ 18:26:00
31. Bojanowska -> Muchobór Wielki @ 23:48:00
32. Dolnobrzeska -> Kośnego (Jarnołtowska) @ 07:43:00
33. Gąsiorów -> Przystankowa @ 23:46:00
34. Obornicka (Wołowska) -> Zalewowa @ 16:33:00
35. Starodworska -> Lutosławskiego @ 15:14:00
36. Bąków -> Stanisławowska (W.K. Formaty) @ 11:57:00
37. Kwidzyńska -> Wejherowska (Hala Orbita) @ 20:19:00
38. Fieldorfa -> Raków IV @ 18:17:00
39. Gromadzka -> Biskupice Podg. LG Electronics @ 05:11:00
40. Aleja Pracy -> Obornicka (Obwodnica) @ 05:50:00
41. OSOBOWICKA (Cmentarz) -> Nowy Dom @ 20:58:00
42. Miodowa -> Raków III @ 19:12:00
43. Biskupice Podg. LG Energy Solution Wr. I -> Wilczyce - Borowa @ 08:10:00
44. Parafialna -> Ożynowa @ 19:36:00
45. Kościuszki -> Głubczycka @ 09:47:00
46. Swojczyce -> Niedziałkowskiego @ 15:31:00
47. Stępin -> ROD Źródło Zdrowia @ 20:25:00
48. Maślicka (Staw) -> Rubczaka @ 19:31:00
49. Połabian -> Nowa Wieś Wr. - pętla @ 15:31:00
50. Zagrodnicza -> Pasikurowice - cmentarz @ 10:48:00


## RESULTS dijkstra_heapq
- Total time: 40.6551
- Mean time per route: 0.8131
- Mean visited nodes: 407.4200
- Mean path nodes: 22.2400
- Failed: 5

## RESULTS a_star cost 0
- Total time: 51.8720
- Mean time per route: 1.0374
- Mean visited nodes: 407.4200
- Mean path nodes: 22.2400
- Failed: 5


## RESULTS a_star cost 500
- Total time: 10.1340
- Mean time per route: 0.2027
- Mean visited nodes: 85.0600
- Mean path nodes: 22.3400
- Failed: 5

##  RESULTS a_star cost 1500
- Total time: 6.2721
- Mean time per route: 0.1254
- Mean visited nodes: 54.3000
- Mean path nodes: 23.3200
- Failed: 5


## RESULTS a_star cost 2000
- Total time: 7.5610
- Mean time per route: 0.1512
- Mean visited nodes: 53.3800
- Mean path nodes: 23.0200
- Failed: 5