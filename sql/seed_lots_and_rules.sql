-- Seed parking lots from Diego's campus map dataset, then build lot rules, occupancy history, and sample tickets.

INSERT INTO parking_lots
    (polygon_id, lot_name, zone, latitude, longitude, capacity, current_occupancy, ev_charger_count, is_active)
VALUES
    ('fac_1', 'Meek West', 'Faculty', 34.36719100, -89.53730900, 141, 91, 1, TRUE),
    ('fac_2', 'Tad Smith North', 'Faculty', 34.36313000, -89.53922300, 192, 60, 1, TRUE),
    ('fac_3', 'Old Athletics', 'Faculty', 34.36350700, -89.53853800, 64, 28, 0, TRUE),
    ('fac_4', 'Tad Smith', 'Faculty', 34.36301600, -89.53956100, 7, 2, 0, TRUE),
    ('fac_5', 'Tad Smith', 'Faculty', 34.36166100, -89.53913000, 13, 9, 0, TRUE),
    ('fac_6', 'Turner West', 'Faculty', 34.36346600, -89.53782800, 30, 20, 0, TRUE),
    ('fac_7', 'Turner West', 'Faculty', 34.36390300, -89.53763100, 5, 3, 0, TRUE),
    ('fac_8', 'Turner Rear', 'Faculty', 34.36321400, -89.53775200, 5, 1, 0, TRUE),
    ('fac_9', 'Turner Rear', 'Faculty', 34.36300500, -89.53749100, 7, 3, 0, TRUE),
    ('fac_10', 'Turner Rear', 'Faculty', 34.36291200, -89.53720100, 5, 1, 0, TRUE),
    ('fac_11', 'Law School South', 'Faculty', 34.36194500, -89.54221300, 95, 39, 0, TRUE),
    ('fac_12', 'Law School', 'Faculty', 34.36318600, -89.54253000, 5, 2, 0, TRUE),
    ('fac_13', 'NCPA', 'Faculty', 34.36042500, -89.54266200, 26, 8, 0, TRUE),
    ('fac_14', 'Faculty Row - RC West', 'Faculty', 34.36784500, -89.53114800, 23, 9, 0, TRUE),
    ('fac_15', 'Faculty Row - RC West', 'Faculty', 34.36772700, -89.53093000, 23, 15, 0, TRUE),
    ('fac_16', 'Faculty Row', 'Faculty', 34.36730100, -89.53086300, 39, 23, 0, TRUE),
    ('fac_17', 'Sorority Circle', 'Faculty', 34.36740900, -89.53243700, 18, 7, 0, TRUE),
    ('fac_18', 'Barnard Observatory Rear', 'Faculty', 34.36738600, -89.53304900, 17, 10, 0, TRUE),
    ('fac_19', 'Yerby', 'Faculty', 34.36522200, -89.53063600, 5, 3, 0, TRUE),
    ('fac_20', 'Yerby', 'Faculty', 34.36538100, -89.53027700, 47, 14, 0, TRUE),
    ('fac_21', 'Yerby', 'Faculty', 34.36593100, -89.52991100, 50, 37, 0, TRUE),
    ('fac_22', 'Yerby', 'Faculty', 34.36609300, -89.53022800, 8, 5, 0, TRUE),
    ('fac_23', 'Music Bldg. East', 'Faculty', 34.36463600, -89.52736000, 26, 12, 0, TRUE),
    ('fac_24', 'Music Bldg. East', 'Faculty', 34.36437800, -89.52717200, 72, 27, 0, TRUE),
    ('fac_25', 'Memory House', 'Faculty', 34.36374200, -89.52606700, 57, 53, 0, TRUE),
    ('fac_26', 'Mary Buie Museum', 'Faculty', 34.36391800, -89.52558700, 47, 22, 0, TRUE),
    ('fac_27', 'Mary Buie Museum', 'Faculty', 34.36423900, -89.52503600, 14, 4, 0, TRUE),
    ('fac_28', 'North Ln - On Street', 'Faculty', 34.36757600, -89.53357000, 5, 1, 0, TRUE),
    ('fac_29', 'Lenoir Hall', 'Faculty', 34.36872100, -89.53339100, 13, 9, 0, TRUE),
    ('fac_30', 'Lenoir Hall', 'Faculty', 34.36878700, -89.53337600, 11, 6, 0, TRUE),
    ('fac_31', 'Meek East', 'Faculty', 34.36743400, -89.53577900, 44, 32, 0, TRUE),
    ('fac_32', 'Magnolia Drive', 'Faculty', 34.36596500, -89.54106500, 137, 96, 1, TRUE),
    ('fac_33', 'Guyton East', 'Faculty', 34.36573600, -89.54227200, 27, 16, 0, TRUE),
    ('fac_34', 'Powers', 'Faculty', 34.36640400, -89.54187100, 43, 35, 0, TRUE),
    ('fac_35', 'Guyton West', 'Faculty', 34.36613500, -89.54377800, 36, 18, 0, TRUE),
    ('fac_36', 'Track', 'Faculty', 34.36012500, -89.53806900, 10, 6, 0, TRUE),
    ('fac_37', 'Procurement', 'Faculty', 34.35832000, -89.54008600, 59, 44, 0, TRUE),
    ('fac_38', 'Procurement', 'Faculty', 34.35812600, -89.53981900, 8, 5, 0, TRUE),
    ('fac_39', 'SBA', 'Faculty', 34.35827700, -89.54106300, 38, 29, 0, TRUE),
    ('fac_40', 'Food Srv. Mgmt.', 'Faculty', 34.35852700, -89.54182300, 45, 27, 0, TRUE),
    ('fac_41', 'Food Srv. Mgmt.', 'Faculty', 34.35873000, -89.54233200, 25, 17, 0, TRUE),
    ('fac_42', 'Insight Park', 'Faculty', 34.35796000, -89.54793800, 70, 22, 0, TRUE),
    ('fac_43', 'Insight Park', 'Faculty', 34.35794300, -89.54872600, 49, 20, 0, TRUE),
    ('fac_44', 'Insight Park', 'Faculty', 34.35839200, -89.54911100, 15, 6, 0, TRUE),
    ('fac_45', 'Medicinal Plant Farm', 'Faculty', 34.35829900, -89.55084100, 18, 6, 0, TRUE),
    ('fac_46', 'Medicinal Plant Farm', 'Faculty', 34.35864300, -89.55103700, 18, 7, 0, TRUE),
    ('fac_47', 'Medicinal Plant Farm', 'Faculty', 34.35809700, -89.55355000, 17, 6, 0, TRUE),
    ('fac_48', 'Waller Research Center', 'Faculty', 34.35948000, -89.54874700, 40, 18, 0, TRUE),
    ('fac_49', 'Physical Plant', 'Faculty', 34.36076700, -89.54811500, 30, 19, 0, TRUE),
    ('fac_50', 'Physical Plant', 'Faculty', 34.36011300, -89.54906600, 157, 78, 1, TRUE),
    ('fac_51', 'Physical Plant', 'Faculty', 34.36008400, -89.54872500, 105, 52, 1, TRUE),
    ('fac_52', 'Physical Plant', 'Faculty', 34.36048500, -89.54862300, 5, 2, 0, TRUE),
    ('fac_53', 'Physical Plant', 'Faculty', 34.36058400, -89.54904500, 16, 7, 0, TRUE),
    ('fac_54', 'Johnny Williams Generation Plant', 'Faculty', 34.35958800, -89.53363500, 5, 4, 0, TRUE),
    ('fac_55', 'Johnny Williams Generation Plant', 'Faculty', 34.35998500, -89.53362200, 5, 3, 0, TRUE),
    ('fac_56', 'Baseball', 'Faculty', 34.36160700, -89.53012500, 44, 27, 0, TRUE),
    ('fac_57', 'Hill North - On Street', 'Faculty', 34.36135900, -89.53765200, 10, 3, 0, TRUE),
    ('fac_58', 'Howry-Falkner', 'Faculty', 34.36700700, -89.53849800, 100, 70, 1, TRUE),
    ('fac_59', 'Bishop', 'Faculty', 34.36537100, -89.53977700, 88, 34, 0, TRUE),
    ('fac_60', 'Music Bldg. Rear', 'Faculty', 34.36395100, -89.52894000, 24, 12, 0, TRUE),
    ('fac_61', 'Music Bldg. Rear', 'Faculty', 34.36370100, -89.52850400, 5, 4, 0, TRUE),
    ('fac_62', 'Health Center', 'Faculty', 34.36782600, -89.53703500, 29, 18, 0, TRUE),
    ('fac_63', 'Cross Street - On Street', 'Faculty', 34.36669900, -89.53730900, 12, 7, 0, TRUE),
    ('fac_64', 'Cross Street - On Street', 'Faculty', 34.36715400, -89.53576400, 5, 3, 0, TRUE),
    ('fac_65', 'Cross Street - On Street', 'Faculty', 34.36708100, -89.53575200, 5, 3, 0, TRUE),
    ('fac_66', 'Cross Street - On Street', 'Faculty', 34.36685700, -89.53578700, 5, 3, 0, TRUE),
    ('fac_67', 'Cross Street - On Street', 'Faculty', 34.36677100, -89.53588300, 5, 2, 0, TRUE),
    ('fac_68', 'Dormitory Row West - West End', 'Faculty', 34.36680400, -89.54136300, 81, 25, 0, TRUE),
    ('fac_69', 'Baxter Hall', 'Faculty', 34.36701600, -89.54195300, 7, 3, 0, TRUE),
    ('fac_70', 'Bishop - On Street', 'Faculty', 34.36464600, -89.53901000, 5, 2, 0, TRUE),
    ('fac_71', 'Bishop - On Street', 'Faculty', 34.36459800, -89.53881700, 5, 2, 0, TRUE),
    ('fac_72', 'Honors College', 'Faculty', 34.36742200, -89.53140800, 5, 4, 0, TRUE),
    ('fac_73', 'Farley/Lamar Hall', 'Faculty', 34.36679100, -89.53181800, 21, 16, 0, TRUE),
    ('fac_74', 'Farley/Lamar Hall', 'Faculty', 34.36705200, -89.53158400, 16, 7, 0, TRUE),
    ('fac_75', 'Farley/Lamar Hall', 'Faculty', 34.36718400, -89.53143800, 5, 3, 0, TRUE),
    ('fac_76', 'Farley/Lamar Hall', 'Faculty', 34.36734600, -89.53122100, 10, 5, 0, TRUE),
    ('fac_77', 'Coulter Rear', 'Faculty', 34.36427500, -89.53185000, 5, 4, 0, TRUE),
    ('fac_78', 'Poole Dr. East - On Street', 'Faculty', 34.36423900, -89.53873700, 5, 2, 0, TRUE),
    ('fac_79', 'Housing Service', 'Faculty', 34.37033700, -89.53896800, 25, 11, 0, TRUE),
    ('fac_80', 'Housing Service', 'Faculty', 34.37025900, -89.53855900, 27, 11, 0, TRUE),
    ('fac_81', 'Library Annex', 'Faculty', 34.36363600, -89.53171600, 135, 82, 1, TRUE),
    ('fac_82', 'South Athletics Lot', 'Faculty', 34.36254600, -89.53252300, 215, 95, 3, TRUE),
    ('fac_83', 'Athletics', 'Faculty', 34.36332400, -89.53224600, 28, 17, 0, TRUE),
    ('fac_84', 'Athletics', 'Faculty', 34.36305600, -89.53317300, 27, 21, 0, TRUE),
    ('fac_85', 'Athletics', 'Faculty', 34.36309400, -89.53286400, 43, 22, 0, TRUE),
    ('fac_86', 'Athletics', 'Faculty', 34.36367000, -89.53261800, 6, 2, 0, TRUE),
    ('fac_87', 'Jackson Avenue Center', 'Faculty', 34.37051300, -89.54515900, 39, 33, 0, TRUE),
    ('fac_88', 'Ford Center/Depot', 'Faculty', 34.36766000, -89.52781100, 6, 3, 0, TRUE),
    ('fac_89', 'Turner South/Tennis', 'Faculty', 34.36222600, -89.53749100, 119, 41, 1, TRUE),
    ('fac_90', 'Manning West', 'Faculty', 34.36069600, -89.53660700, 64, 20, 0, TRUE),
    ('fac_91', 'South Generation Plant', 'Faculty', 34.35859500, -89.53342700, 94, 33, 0, TRUE),
    ('fac_92', 'JAC North', 'Faculty', 34.37167200, -89.54683700, 30, 19, 0, TRUE),
    ('fac_93', 'Rebel Drive-Dorm Row North On Street', 'Faculty', 34.36644400, -89.53779300, 5, 3, 0, TRUE),
    ('fac_94', 'North Lane', 'Faculty', 34.36865300, -89.53359300, 7, 3, 0, TRUE),
    ('fac_95', 'Jackson Avenue Center', 'Faculty', 34.37072800, -89.54852300, 106, 35, 1, TRUE),
    ('fac_96', 'RC West', 'Faculty', 34.36758100, -89.53043500, 28, 14, 0, TRUE),
    ('fac_97', 'Jackson Avenue Center', 'Faculty', 34.37060500, -89.54660300, 9, 7, 0, TRUE),
    ('fac_98', 'South Campus Rec. Facility', 'Faculty', 34.35401200, -89.54025700, 114, 67, 1, TRUE),
    ('fac_99', 'SOC-Underbuilding', 'Faculty', 34.34909000, -89.51898500, 47, 39, 0, TRUE),
    ('fac_100', 'Guyton West', 'Faculty', 34.36637100, -89.54386700, 32, 24, 0, TRUE),
    ('fac_101', 'Ridge North', 'Faculty', 34.36842500, -89.53808700, 53, 16, 0, TRUE),
    ('com_bl1', 'Tad Smith Valley Lot', 'Commuter Blue', 34.36281300, -89.53864500, 66, 45, 0, TRUE),
    ('com_bl2', 'Tad Smith Valley Lot', 'Commuter Blue', 34.36162700, -89.53825600, 188, 126, 1, TRUE),
    ('com_bl3', 'Tad Smith South', 'Commuter Blue', 34.36119600, -89.53997300, 69, 41, 0, TRUE),
    ('com_bl4', 'Tad Smith South', 'Commuter Blue', 34.36114200, -89.53973800, 80, 35, 0, TRUE),
    ('com_bl5', 'Tad Smith NCPA', 'Commuter Blue', 34.36163400, -89.54057500, 76, 49, 0, TRUE),
    ('com_bl6', 'Tad Smith Northwest', 'Commuter Blue', 34.36294900, -89.54087200, 79, 28, 0, TRUE),
    ('com_bl7', 'Tad Smith Northwest', 'Commuter Blue', 34.36316200, -89.54069800, 74, 39, 0, TRUE),
    ('com_bl8', 'Tad Smith Northwest', 'Commuter Blue', 34.36313800, -89.54044100, 62, 34, 0, TRUE),
    ('com_bl9', 'Tad Smith Northwest', 'Commuter Blue', 34.36309100, -89.54016000, 43, 40, 0, TRUE),
    ('com_bl10', 'Tad Smith Northwest', 'Commuter Blue', 34.36232800, -89.54066000, 5, 3, 0, TRUE),
    ('com_bl11', 'Tad Smith Northwest', 'Commuter Blue', 34.36243100, -89.54024100, 5, 2, 0, TRUE),
    ('com_bl12', 'Law School North', 'Commuter Blue', 34.36327200, -89.54169400, 76, 43, 0, TRUE),
    ('com_bl13', 'Law School North', 'Commuter Blue', 34.36337900, -89.54306500, 66, 26, 0, TRUE),
    ('com_bl14', 'Law School North', 'Commuter Blue', 34.36357100, -89.54293200, 72, 57, 0, TRUE),
    ('com_bl15', 'Law School North', 'Commuter Blue', 34.36374100, -89.54288200, 72, 56, 0, TRUE),
    ('com_bl16', 'Law School North', 'Commuter Blue', 34.36393400, -89.54297500, 58, 26, 0, TRUE),
    ('com_bl17', 'West Road Lot', 'Commuter Blue', 34.36440800, -89.54366100, 71, 46, 0, TRUE),
    ('com_bl18', 'West Road Lot', 'Commuter Blue', 34.36525400, -89.54362700, 94, 59, 0, TRUE),
    ('com_bl19', 'Tad Smith', 'Commuter Blue', 34.36224500, -89.53877400, 33, 12, 0, TRUE),
    ('com_bl20', 'Tad Smith', 'Commuter Blue', 34.36219000, -89.53995800, 36, 25, 0, TRUE),
    ('com_bl21', 'Tad Smith', 'Commuter Blue', 34.36289400, -89.53980000, 11, 6, 0, TRUE),
    ('com_bl22', 'Track', 'Commuter Blue', 34.35986800, -89.53834100, 66, 48, 0, TRUE),
    ('com_bl23', 'Baseball North', 'Commuter Blue', 34.36327600, -89.52915600, 118, 69, 1, TRUE),
    ('com_bl24', 'West Music', 'Commuter Blue', 34.36402900, -89.53001200, 94, 28, 0, TRUE),
    ('com_bl25', 'West Music', 'Commuter Blue', 34.36375200, -89.53037900, 42, 20, 0, TRUE),
    ('com_bl26', 'West Music', 'Commuter Blue', 34.36313400, -89.53003100, 28, 8, 0, TRUE),
    ('com_bl27', 'West Music', 'Commuter Blue', 34.36317500, -89.53041200, 139, 112, 1, TRUE),
    ('com_bl28', 'Law School South', 'Commuter Blue', 34.36186200, -89.54337400, 41, 32, 0, TRUE),
    ('com_bl29', 'West Music', 'Commuter Blue', 34.36294800, -89.53083400, 86, 65, 0, TRUE),
    ('com_bl30', 'West Music', 'Commuter Blue', 34.36221700, -89.53053300, 52, 24, 0, TRUE),
    ('com_bl31', 'University Place - On Street', 'Commuter Blue', 34.36060800, -89.53098100, 135, 44, 1, TRUE),
    ('com_bl32', 'University Place - On Street', 'Commuter Blue', 34.36306700, -89.52984800, 57, 44, 0, TRUE),
    ('com_bl33', 'University Place - On Street', 'Commuter Blue', 34.36266000, -89.53003000, 48, 39, 0, TRUE),
    ('com_bl34', 'University Place - On Street', 'Commuter Blue', 34.36371800, -89.52973000, 28, 9, 0, TRUE),
    ('com_bl35', 'Taylor RV', 'Commuter Blue', 34.36140300, -89.53108200, 97, 55, 0, TRUE),
    ('com_bl36', 'Ford Center/Depot', 'Commuter Blue', 34.36587300, -89.52776900, 117, 39, 1, TRUE),
    ('com_bl37', 'Ford Center/Depot', 'Commuter Blue', 34.36607800, -89.52844000, 46, 33, 0, TRUE),
    ('com_bl38', 'Ford Center/Depot', 'Commuter Blue', 34.36607300, -89.52830300, 9, 6, 0, TRUE),
    ('com_bl39', 'Ford Center/Depot', 'Commuter Blue', 34.36629300, -89.52810600, 53, 19, 0, TRUE),
    ('com_bl40', 'Ford Center/Depot', 'Commuter Blue', 34.36660700, -89.52771500, 17, 9, 0, TRUE),
    ('com_bl41', 'Ford Center/Depot', 'Commuter Blue', 34.36696600, -89.52782900, 35, 21, 0, TRUE),
    ('com_bl42', 'Ford Center/Depot', 'Commuter Blue', 34.36689600, -89.52823600, 72, 32, 0, TRUE),
    ('com_bl43', 'Ford Center/Depot', 'Commuter Blue', 34.36679300, -89.52813500, 12, 9, 0, TRUE),
    ('com_bl44', 'Ford Center/Depot', 'Commuter Blue', 34.36694100, -89.52846500, 72, 38, 0, TRUE),
    ('com_bl45', 'Ford Center', 'Commuter Blue', 34.36649500, -89.52888500, 5, 2, 0, TRUE),
    ('com_bl46', 'Hill Drive Lot', 'Commuter Blue', 34.36038500, -89.53842300, 46, 27, 0, TRUE),
    ('com_bl47', 'Manning Center', 'Commuter Blue', 34.36007600, -89.53518300, 265, 185, 3, TRUE),
    ('com_bl48', 'Village North', 'Commuter Blue', 34.36306000, -89.54394300, 68, 27, 0, TRUE),
    ('com_bl49', 'Tad Smith NCPA', 'Commuter Blue', 34.36174700, -89.54079500, 57, 26, 0, TRUE),
    ('com_bl50', 'Jeannette Phillips Parking Lot', 'Commuter Blue', 34.35892100, -89.53915900, 422, 390, 3, TRUE),
    ('com_rd1', 'South Lot', 'Commuter Red', 34.35711400, -89.53675100, 101, 66, 1, TRUE),
    ('com_rd2', 'South Lot', 'Commuter Red', 34.35699300, -89.53710700, 120, 64, 1, TRUE),
    ('com_rd3', 'South Lot', 'Commuter Red', 34.35724000, -89.53483000, 142, 83, 1, TRUE),
    ('com_rd4', 'South Lot', 'Commuter Red', 34.35703100, -89.53520900, 145, 53, 1, TRUE),
    ('com_rd5', 'South Lot', 'Commuter Red', 34.35686700, -89.53520700, 148, 62, 1, TRUE),
    ('com_rd6', 'South Lot', 'Commuter Red', 34.35665600, -89.53441700, 140, 68, 1, TRUE),
    ('com_rd7', 'South Lot', 'Commuter Red', 34.35726000, -89.53291300, 56, 34, 0, TRUE),
    ('com_rd8', 'South Lot', 'Commuter Red', 34.35707500, -89.53287100, 61, 26, 0, TRUE),
    ('com_rd9', 'South Lot', 'Commuter Red', 34.35685800, -89.53318500, 27, 11, 0, TRUE),
    ('com_rd10', 'South Lot', 'Commuter Red', 34.35669400, -89.53329400, 39, 13, 0, TRUE),
    ('com_rd11', 'Jackson Avenue Center', 'Commuter Red', 34.37047600, -89.54569200, 323, 209, 3, TRUE),
    ('com_rd12', 'Jackson Avenue Center', 'Commuter Red', 34.37014300, -89.54711800, 500, 212, 3, TRUE),
    ('com_rd13', 'JAC Bank Lot', 'Commuter Red', 34.36980200, -89.54545000, 154, 122, 1, TRUE),
    ('com_rd14', 'South Campus Rec. Facility', 'Commuter Red', 34.35454300, -89.53999600, 96, 74, 0, TRUE),
    ('com_rd15', 'South Campus Rec. Facility', 'Commuter Red', 34.35418600, -89.54224500, 284, 96, 3, TRUE),
    ('com_rd16', 'Soccer', 'Commuter Red', 34.35790500, -89.54723700, 66, 28, 0, TRUE),
    ('com_rd17', 'Soccer', 'Commuter Red', 34.35858000, -89.54717200, 47, 31, 0, TRUE),
    ('com_rd18', 'Softball', 'Commuter Red', 34.35947100, -89.54419300, 35, 14, 0, TRUE),
    ('com_rd19', 'Gillom Sports', 'Commuter Red', 34.35796700, -89.54472600, 109, 40, 1, TRUE),
    ('com_rd20', 'Basketball Practice Facility', 'Commuter Red', 34.35839600, -89.54363600, 58, 47, 0, TRUE),
    ('com_rd21', 'Basketball Practice Facility', 'Commuter Red', 34.35792900, -89.54275900, 5, 3, 0, TRUE),
    ('com_rd22', 'Basketball Practice Facility', 'Commuter Red', 34.35800300, -89.54263100, 5, 2, 0, TRUE),
    ('com_rd23', 'Basketball Practice Facility', 'Commuter Red', 34.35867100, -89.54266300, 5, 3, 0, TRUE),
    ('com_rd24', 'Basketball Practice Facility', 'Commuter Red', 34.35859900, -89.54274800, 5, 3, 0, TRUE),
    ('com_rd25', 'East Track', 'Commuter Red', 34.35828000, -89.53723300, 8, 3, 0, TRUE),
    ('com_rd26', 'East Track', 'Commuter Red', 34.35837400, -89.53701700, 22, 7, 0, TRUE),
    ('com_rd27', 'East Track', 'Commuter Red', 34.35850100, -89.53678300, 33, 17, 0, TRUE),
    ('com_rd28', 'East Track', 'Commuter Red', 34.35863600, -89.53655600, 46, 24, 0, TRUE),
    ('com_rd29', 'East Track', 'Commuter Red', 34.35870800, -89.53633000, 59, 32, 0, TRUE),
    ('com_rd30', 'Intramural Fields', 'Commuter Red', 34.35976100, -89.56023700, 86, 60, 0, TRUE),
    ('com_rd31', 'Intramural Fields', 'Commuter Red', 34.35937200, -89.55897900, 69, 46, 0, TRUE),
    ('com_rd32', 'Village South', 'Commuter Red', 34.36050800, -89.54354500, 44, 41, 0, TRUE),
    ('com_rd33', 'SOC - North', 'Commuter Red', 34.34950400, -89.51936600, 60, 21, 0, TRUE),
    ('com_rd34', 'SOC - East', 'Commuter Red', 34.34880600, -89.51865500, 9, 4, 0, TRUE),
    ('com_rd35', 'SOC - South', 'Commuter Red', 34.34781000, -89.52050600, 224, 109, 3, TRUE),
    ('com_rd36', 'SOC - Garage', 'Commuter Red', 34.34745700, -89.51965000, 337, 260, 6, TRUE),
    ('com_rd37', 'Insight Park - Mixed ', 'Commuter Red', 34.35783400, -89.54783100, 75, 32, 0, TRUE),
    ('com_rd38', 'Commuter Red (JAC Danvers Lot)', 'Commuter Red', 34.36933800, -89.54650600, 195, 78, 1, TRUE),
    ('res_cw1', 'Campus Walk', 'Campus Walk', 34.36346100, -89.54802200, 287, 156, 3, TRUE),
    ('res_cw2', 'Campus Walk', 'Campus Walk', 34.36385800, -89.54827600, 284, 151, 3, TRUE),
    ('res_ea1', 'RC/Alumni Drive', 'Residential East', 34.36770100, -89.52955300, 114, 51, 1, TRUE),
    ('res_ea2', 'RC West', 'Residential East', 34.36784300, -89.53017500, 29, 12, 0, TRUE),
    ('res_ea3', 'RC West', 'Residential East', 34.36805300, -89.53030700, 49, 39, 0, TRUE),
    ('res_ea4', 'RC North', 'Residential East', 34.36977500, -89.53068800, 81, 44, 0, TRUE),
    ('res_ea5', 'RC West', 'Residential East', 34.36859900, -89.52973700, 75, 58, 0, TRUE),
    ('res_ea6', 'RC North', 'Residential East', 34.36938300, -89.53009100, 87, 52, 0, TRUE),
    ('res_ea7', 'RC North', 'Residential East', 34.36936300, -89.53056200, 5, 1, 0, TRUE),
    ('res_ea8', 'Silver Pond', 'Residential East', 34.36958500, -89.53238000, 46, 43, 0, TRUE),
    ('res_ea9', 'Silver Pond', 'Residential East', 34.36962600, -89.53214800, 41, 31, 0, TRUE),
    ('res_ea10', 'Sorority', 'Residential East', 34.36876200, -89.53252900, 39, 32, 0, TRUE),
    ('res_ea11', 'Sorority', 'Residential East', 34.36894700, -89.53227700, 37, 29, 0, TRUE),
    ('res_ea12', 'Sorority', 'Residential East', 34.36892700, -89.53205000, 54, 41, 0, TRUE),
    ('res_ea13', 'Sorority Circle', 'Residential East', 34.36772600, -89.53250000, 57, 22, 0, TRUE),
    ('res_ea14', 'Sorority Row-On Street', 'Residential East', 34.36765900, -89.53288400, 11, 6, 0, TRUE),
    ('res_ea15', 'Sorority Row-On Street', 'Residential East', 34.36831500, -89.53287700, 9, 3, 0, TRUE),
    ('res_ea16', 'Sorority Row-On Street', 'Residential East', 34.36879400, -89.53285700, 11, 5, 0, TRUE),
    ('res_ea17', 'Northgate Square', 'Residential East', 34.36979600, -89.53382100, 9, 2, 0, TRUE),
    ('res_ea18', 'Northgate Square', 'Residential East', 34.36976200, -89.53375000, 9, 4, 0, TRUE),
    ('res_ea19', 'Northgate Square', 'Residential East', 34.37029300, -89.53359100, 20, 16, 0, TRUE),
    ('res_ea20', 'Northgate Square RH ADA', 'Residential East', 34.37035400, -89.53368000, 16, 7, 0, TRUE),
    ('res_ea21', 'Northgate Square', 'Residential East', 34.37044800, -89.53290100, 17, 12, 0, TRUE),
    ('res_ea22', 'Northgate Square', 'Residential East', 34.37052200, -89.53300900, 13, 7, 0, TRUE),
    ('res_ea23', 'RH', 'Residential East', 34.37100400, -89.53405600, 32, 17, 0, TRUE),
    ('res_ce1', 'Crosby Hall', 'Residential Central', 34.36958100, -89.53447100, 5, 4, 0, TRUE),
    ('res_ce2', 'Crosby Hall', 'Residential Central', 34.36991100, -89.53439500, 11, 9, 0, TRUE),
    ('res_ce3', 'Crosby Hall', 'Residential Central', 34.37096300, -89.53445700, 405, 245, 3, TRUE),
    ('res_ce4', 'Crosby East - On Curb', 'Residential Central', 34.37002300, -89.53430800, 7, 4, 0, TRUE),
    ('res_ce5', 'Brown Hall', 'Residential Central', 34.36927800, -89.53394700, 51, 19, 0, TRUE),
    ('res_ce6', 'Womens Terrace Lots', 'Residential Central', 34.36859200, -89.53469500, 124, 57, 1, TRUE),
    ('res_ce7', 'Stewart West', 'Residential Central', 34.36857300, -89.53604600, 31, 25, 0, TRUE),
    ('res_ce8', 'Stewart West', 'Residential Central', 34.36858100, -89.53576200, 5, 3, 0, TRUE),
    ('res_ce9', 'Womens Terrace - On Street', 'Residential Central', 34.36810300, -89.53401200, 10, 5, 0, TRUE),
    ('res_ce10', 'Womens Terrace - On Street', 'Residential Central', 34.36860800, -89.53429700, 56, 39, 0, TRUE),
    ('res_ce11', 'Womens Terrace - On Street', 'Residential Central', 34.36894000, -89.53444700, 6, 1, 0, TRUE),
    ('res_ce12', 'Womens Terrace - On Street', 'Residential Central', 34.36886000, -89.53518500, 8, 4, 0, TRUE),
    ('res_ce13', 'Womens Terrace - On Street', 'Residential Central', 34.36853100, -89.53514400, 48, 27, 0, TRUE),
    ('res_nw1', 'Stockard/Martin - North', 'Residential Northwest', 34.37139900, -89.53738400, 134, 103, 1, TRUE),
    ('res_nw2', 'Stockard/Martin - East', 'Residential Northwest', 34.37158500, -89.53598700, 25, 9, 0, TRUE),
    ('res_nw3', 'Stockard/Martin - North', 'Residential Northwest', 34.37139600, -89.53719900, 54, 44, 0, TRUE),
    ('res_nw4', 'Stockard/Martin - South', 'Residential Northwest', 34.37016200, -89.53780600, 33, 11, 0, TRUE),
    ('res_nw5', 'Stockard/Martin - South', 'Residential Northwest', 34.37013700, -89.53761700, 39, 15, 0, TRUE),
    ('res_nw6', 'Stockard/Martin - South', 'Residential Northwest', 34.37009500, -89.53733400, 46, 28, 0, TRUE),
    ('res_nw7', 'Stockard/Martin - South', 'Residential Northwest', 34.37010500, -89.53712200, 50, 33, 0, TRUE),
    ('res_nw8', 'Stockard/Martin - South', 'Residential Northwest', 34.36999500, -89.53684500, 55, 23, 0, TRUE),
    ('res_nw9', 'Stockard/Martin - South', 'Residential Northwest', 34.37009000, -89.53661700, 48, 17, 0, TRUE),
    ('res_nw10', 'Stockard/Martin - South', 'Residential Northwest', 34.36959800, -89.53726000, 27, 21, 0, TRUE),
    ('res_nw11', 'Stockard/Martin West - On Curb', 'Residential Northwest', 34.37061100, -89.53792200, 5, 2, 0, TRUE),
    ('res_nw12', 'Stockard/Martin - East', 'Residential Northwest', 34.37048700, -89.53642500, 5, 3, 0, TRUE),
    ('res_nw13', 'Stockard/Martin - South', 'Residential Northwest', 34.37053000, -89.53715300, 5, 3, 0, TRUE),
    ('res_nw14', 'Stockard/Martin - North', 'Residential Northwest', 34.37113700, -89.53680000, 5, 2, 0, TRUE),
    ('res_nw15', 'Stockard/Martin - North', 'Residential Northwest', 34.37113300, -89.53752400, 5, 3, 0, TRUE),
    ('res_so1', 'Fraternity Row Tennis', 'Residential South', 34.36522900, -89.54151300, 36, 21, 0, TRUE),
    ('res_so2', 'Fraternity Alley East', 'Residential South', 34.36465200, -89.54108200, 38, 30, 0, TRUE),
    ('res_so3', 'Fraternity Alley East', 'Residential South', 34.36435200, -89.54064700, 55, 22, 0, TRUE),
    ('res_so4', 'Fraternity Alley West', 'Residential South', 34.36452100, -89.54163100, 33, 22, 0, TRUE),
    ('res_so5', 'Fraternity Alley West', 'Residential South', 34.36461900, -89.54256600, 46, 19, 0, TRUE),
    ('res_so6', 'West Road Fraternity', 'Residential South', 34.36543000, -89.54334500, 9, 4, 0, TRUE),
    ('res_so7', 'West Road Fraternity', 'Residential South', 34.36530000, -89.54317800, 8, 5, 0, TRUE),
    ('res_so8', 'Poole Dr. West - On Street', 'Residential South', 34.36416800, -89.54306300, 19, 8, 0, TRUE),
    ('res_so9', 'Poole Dr. West - On Street', 'Residential South', 34.36396400, -89.54210900, 30, 14, 0, TRUE),
    ('res_so10', 'Poole Dr. West - On Street', 'Residential South', 34.36381100, -89.54177600, 10, 7, 0, TRUE),
    ('res_so11', 'Poole Dr. East - On Street', 'Residential South', 34.36367100, -89.54056600, 16, 5, 0, TRUE),
    ('res_so12', 'Poole Dr. East - On Street', 'Residential South', 34.36364600, -89.54098100, 7, 3, 0, TRUE),
    ('res_so13', 'Poole Dr. East - On Street', 'Residential South', 34.36353400, -89.54026600, 8, 6, 0, TRUE),
    ('res_so14', 'Poole Dr. East - On Street', 'Residential South', 34.36394800, -89.53910400, 13, 11, 0, TRUE),
    ('res_so15', 'Poole Dr. East - On Street', 'Residential South', 34.36362400, -89.53969100, 5, 1, 0, TRUE),
    ('res_so16', 'Poole Dr. East - On Street', 'Residential South', 34.36381600, -89.53914400, 12, 5, 0, TRUE),
    ('res_so17', 'Rebel Dr. South', 'Residential South', 34.36765500, -89.54361500, 71, 31, 0, TRUE),
    ('res_so18', 'Guyton West Residential South', 'Residential South', 34.36651300, -89.54376300, 34, 27, 0, TRUE),
    ('res_so19', 'Vaught Lane - Residential South', 'Residential South', 34.36686700, -89.54633000, 37, 29, 0, TRUE),
    ('vis1', 'Old Athletics', 'Visitor', 34.36384200, -89.53865600, 17, 13, 0, TRUE),
    ('vis2', 'Old Athletics', 'Visitor', 34.36407400, -89.53832600, 37, 18, 0, TRUE),
    ('vis3', 'Martindale - On Street', 'Visitor', 34.36434200, -89.53800900, 9, 3, 0, TRUE),
    ('vis4', 'Turner East', 'Visitor', 34.36355200, -89.53667600, 34, 25, 0, TRUE),
    ('vis5', 'Howry-Falkner', 'Visitor', 34.36680400, -89.53796700, 25, 17, 0, TRUE),
    ('vis6', 'Manning Center- Metered', 'Visitor', 34.36014600, -89.53541400, 11, 7, 0, TRUE),
    ('vis7', 'Student Union - Timed Spaces', 'Visitor', 34.36806600, -89.53466300, 94, 87, 0, TRUE),
    ('vis8', 'Alumni Center', 'Visitor', 34.36646300, -89.53061400, 14, 9, 0, TRUE),
    ('vis9', 'SOC - Metered', 'Visitor', 34.34814100, -89.52060600, 8, 2, 0, TRUE),
    ('vis10', 'University Ave.', 'Visitor', 34.36522000, -89.53347600, 80, 59, 0, TRUE),
    ('vis11', 'Willie Price', 'Visitor', 34.36785400, -89.54158700, 18, 8, 0, TRUE),
    ('vis12', 'Mary Buie Museum', 'Visitor', 34.36409500, -89.52550400, 6, 3, 0, TRUE),
    ('vis13', 'Tad Smith', 'Visitor', 34.36166600, -89.53921100, 8, 6, 0, TRUE),
    ('vis14', 'Tad Smith', 'Visitor', 34.36269900, -89.53954300, 7, 2, 0, TRUE),
    ('vis15', 'Martindale', 'Visitor', 34.36496700, -89.53743600, 5, 1, 0, TRUE),
    ('vis16', 'Circle', 'Visitor', 34.36533800, -89.53508300, 238, 85, 3, TRUE);

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Faculty';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Faculty';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CB', 'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Faculty';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CR', 'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Faculty';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Blue';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Blue';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CB', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Blue';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CR', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Blue';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Red';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Red';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CR', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Red';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CB', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Commuter Red';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CW', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Campus Walk';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'RE', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential East';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential East';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'RC', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential Central';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential Central';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'RNW', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential Northwest';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'CB', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential Northwest';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'RS', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential South';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'FS', 'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Residential South';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'VSD', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Visitor';

INSERT INTO parking_rules
    (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed, rule_source)
SELECT lot_id, 'VSD', 'Sat,Sun', '00:00:00', '23:59:59', TRUE, 'seed'
FROM parking_lots
WHERE zone = 'Visitor';


INSERT INTO parking_occupancy_log
    (lot_id, recorded_at, occupancy, ev_chargers_in_use, source)
SELECT
    lot_id,
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    GREATEST(0, LEAST(capacity, FLOOR(current_occupancy * 0.60))),
    LEAST(ev_charger_count, FLOOR(ev_charger_count * 0.34)),
    'seed'
FROM parking_lots;

INSERT INTO parking_occupancy_log
    (lot_id, recorded_at, occupancy, ev_chargers_in_use, source)
SELECT
    lot_id,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    GREATEST(0, LEAST(capacity, FLOOR(current_occupancy * 0.82))),
    LEAST(ev_charger_count, FLOOR(ev_charger_count * 0.67)),
    'seed'
FROM parking_lots;

INSERT INTO parking_occupancy_log
    (lot_id, recorded_at, occupancy, ev_chargers_in_use, source)
SELECT
    lot_id,
    NOW(),
    current_occupancy,
    LEAST(ev_charger_count, GREATEST(0, FLOOR(ev_charger_count * 0.75))),
    'seed'
FROM parking_lots;

INSERT INTO tickets
    (user_id, lot_id, permit_id, issue_date, amount, status, description, offense_type, resolved_date)
VALUES
    ('cb001', (SELECT lot_id FROM parking_lots WHERE polygon_id = 'fac_1'), 'CB', DATE_SUB(NOW(), INTERVAL 6 DAY), 35.00, 'Unpaid', 'Parked in a faculty-only lot during restricted hours.', 'Permit mismatch', NULL),
    ('cr001', (SELECT lot_id FROM parking_lots WHERE polygon_id = 'com_bl12'), 'CR', DATE_SUB(NOW(), INTERVAL 4 DAY), 25.00, 'Pending', 'Vehicle remained in a blue lot after posted window.', 'Zone violation', NULL),
    ('vis001', (SELECT lot_id FROM parking_lots WHERE polygon_id = 'fac_87'), 'VSD', DATE_SUB(NOW(), INTERVAL 2 DAY), 15.00, 'Paid', 'Visitor parked beyond posted time limit.', 'Timed space overstay', DATE_SUB(NOW(), INTERVAL 1 DAY)),
    ('fac001', (SELECT lot_id FROM parking_lots WHERE polygon_id = 'com_rd11'), 'FS', DATE_SUB(NOW(), INTERVAL 8 DAY), 40.00, 'Dismissed', 'Faculty vehicle cited in commuter red overflow during event traffic.', 'Event overflow', DATE_SUB(NOW(), INTERVAL 7 DAY));
