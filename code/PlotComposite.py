import sys
import numpy as np
import wradlib as wrl
import matplotlib.pylab as pl
import matplotlib.pyplot as plt
from pyproj import Proj
import shapefile as shp

from HelperFunctions import max_from_arrays, plot_grid, clutter_gabella, attcorr, rain_depths, quantiles_100
from ReadGaugeData import read_gauges_60min, read_gauges_1min, gaugearray

myProj = Proj("+proj=utm +zone=33 +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

print("Composite and adjustment.")

# Retrieve arguments from shell script.
minutes = int(sys.argv[1])

# Define filenames.
filename_drs = "raa00-dx_10488-1901091200-drs---bin"
filename_pro = "raa00-dx_10392-1901091200-pro---bin"
filename_umd = "raa00-dx_10356-1901091200-umd---bin"
filename_neu = "raa00-dx_10557-1901091200-neu---bin"
filename_eis = "raa00-dx_10780-1901091200-eis---bin"
path_1min = "opendata.dwd.de/climate_environment/CDC/observations_germany/climate/1_minute/precipitation/historical/2019/"
path_60min = "opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/historical/"

# Define radar site location (lon, lat, elev).
radar_location_drs = (13.769722, 51.125278, 263)
radar_location_pro = (13.858212, 52.648667, 194)
radar_location_umd = (11.176091, 52.160096, 185)
radar_location_neu = (11.135034, 50.500114, 880)
radar_location_eis = (12.402788, 49.540667, 799)

# Create polar grid.
elevation = 0.5 # degree
azimuths = np.arange(0,360) # degrees
ranges = np.arange(0, 128000., 1000.) # meters
polargrid = np.meshgrid(ranges, azimuths)

# Create xy grid.
xgrid = np.linspace(-50000, 650000, 700)
ygrid = np.linspace(5350000, 6050000, 700)
grid_xy = np.meshgrid(xgrid, ygrid)
grid_xy = np.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()

def get_gridded_depths(filename, radar_location_latlon, minutes):
    f = wrl.util.get_wradlib_data_file('example_data/'+filename)
    data, metadata = wrl.io.read_dx(f) # Read data
    clmap, data_no_clutter = clutter_gabella(data, filename) # Clutter correction
    att, data_attcorr = attcorr(data_no_clutter, filename) # Attenuation correction
    depths = rain_depths(data_attcorr, filename, minutes) # ZR-Relation
    # Project into xyz-coords.
    coords, rad = wrl.georef.spherical_to_xyz(polargrid[0], polargrid[1], elevation, radar_location_latlon)
    # Reproject and grid into EPSG 32633.
    utm_coords = wrl.georef.reproject(coords, projection_source=rad,projection_target = wrl.georef.epsg_to_osr(32633))
    x = utm_coords[..., 0]
    y = utm_coords[..., 1]
    xy=np.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, 128000., np.array([x.mean(), y.mean()]), depths.ravel(), wrl.ipol.Nearest)
    gridded = gridded.reshape((len(xgrid), len(ygrid)))
    return gridded

gridded_drs = get_gridded_depths(filename_drs, radar_location_drs, minutes)
gridded_eis = get_gridded_depths(filename_eis, radar_location_eis, minutes)
gridded_umd = get_gridded_depths(filename_umd, radar_location_umd, minutes)
gridded_pro = get_gridded_depths(filename_pro, radar_location_pro, minutes)
gridded_neu = get_gridded_depths(filename_neu, radar_location_neu, minutes)

# Fix wrong pixels in umd-radar domain.
for row in range(700):
    for col in range(700):
        if 430 <= row <=439 and 286 <= col <= 303:
            gridded_umd[row][col]=0

# Merge radar domains.      
domain = np.empty((700,700))
domain[:] = np.NaN
domain = max_from_arrays(domain, gridded_drs)
domain = max_from_arrays(domain, gridded_eis)
domain = max_from_arrays(domain, gridded_pro)
domain = max_from_arrays(domain, gridded_umd)
domain = max_from_arrays(domain, gridded_neu)
radar = domain

# Read gauge data.
gauges_in_domain = ['00029', '00046', '00053', '00073', '00087', '00096', '00103', '00118', '00124', '00131', '00151', '00152', '00164', '00191', '00198', '00213', '00222', '00227', '00240', '00246', '00282', '00287', '00294', '00303', '00314', '00320', '00336', '00359', '00360', '00378', '00379', '00399', '00400', '00403', '00410', '00420', '00427', '00430', '00433', '00445', '00504', '00505', '00542', '00550', '00551', '00567', '00589', '00622', '00630', '00633', '00656', '00662', '00714', '00721', '00735', '00753', '00775', '00797', '00807', '00812', '00814', '00815', '00840', '00848', '00853', '00863', '00867', '00874', '00880', '00885', '00896', '00962', '00966', '00970', '00974', '00991', '01001', '01039', '01048', '01050', '01051', '01052', '01067', '01095', '01107', '01119', '01139', '01158', '01161', '01166', '01170', '01207', '01210', '01270', '01278', '01279', '01282', '01297', '01320', '01332', '01350', '01357', '01358', '01392', '01411', '01435', '01441', '01458', '01473', '01497', '01511', '01526', '01542', '01544', '01573', '01578', '01587', '01605', '01607', '01612', '01684', '01689', '01691', '01717', '01721', '01735', '01744', '01770', '01793', '01801', '01810', '01830', '01832', '01846', '01847', '01848', '01869', '01900', '01957', '01997', '02011', '02012', '02014', '02039', '02044', '02064', '02066', '02119', '02152', '02171', '02174', '02175', '02233', '02252', '02261', '02274', '02278', '02294', '02323', '02372', '02376', '02409', '02410', '02431', '02438', '02444', '02503', '02531', '02538', '02541', '02550', '02556', '02562', '02597', '02600', '02618', '02625', '02627', '02641', '02662', '02673', '02680', '02700', '02704', '02709', '02733', '02750', '02779', '02794', '02839', '02856', '02860', '02878', '02884', '02890', '02925', '02928', '02932', '02951', '02958', '02985', '02992', '02997', '03012', '03015', '03034', '03080', '03083', '03093', '03094', '03121', '03126', '03146', '03147', '03148', '03153', '03158', '03166', '03175', '03179', '03181', '03204', '03205', '03207', '03220', '03226', '03231', '03234', '03248', '03271', '03279', '03289', '03297', '03304', '03308', '03348', '03364', '03376', '03426', '03429', '03435', '03438', '03445', '03473', '03478', '03491', '03497', '03509', '03513', '03525', '03536', '03552', '03558', '03560', '03571', '03572', '03607', '03617', '03650', '03667', '03668', '03681', '03700', '03739', '03740', '03811', '03821', '03836', '03844', '03875', '03881', '03886', '03906', '03911', '03946', '03948', '03950', '03967', '03975', '03987', '03999', '04000', '04016', '04023', '04032', '04036', '04052', '04080', '04104', '04109', '04135', '04185', '04218', '04224', '04248', '04280', '04282', '04290', '04303', '04354', '04367', '04377', '04387', '04412', '04445', '04464', '04469', '04480', '04485', '04493', '04494', '04501', '04546', '04548', '04555', '04559', '04566', '04592', '04599', '04601', '04603', '04605', '04618', '04637', '04642', '04651', '04694', '04748', '04752', '04763', '04790', '04801', '04813', '04816', '04818', '04878', '04911', '04912', '04958', '04978', '04982', '04984', '04997', '05002', '05013', '05017', '05023', '05034', '05036', '05046', '05084', '05109', '05142', '05146', '05148', '05149', '05158', '05230', '05279', '05285', '05303', '05335', '05349', '05371', '05382', '05395', '05397', '05401', '05419', '05424', '05440', '05484', '05490', '05546', '05548', '05555', '05573', '05600', '05614', '05629', '05643', '05663', '05676', '05684', '05705', '05729', '05745', '05750', '05762', '05763', '05779', '05797', '05800', '05814', '05825', '05854', '05943', '06093', '06109', '06129', '06161', '06170', '06182', '06191', '06195', '06200', '06215', '06216', '06249', '06252', '06265', '06266', '06268', '06269', '06270', '06271', '06272', '06273', '06281', '06282', '06287', '06296', '06298', '06305', '06312', '06314', '06336', '06338', '06347', '07075', '07077', '07079', '07099', '07244', '07285', '07321', '07323', '07326', '07327', '07328', '07329', '07333', '07334', '07335', '07337', '07343', '07350', '07351', '07361', '07364', '07367', '07368', '07370', '07372', '07389', '07393', '07394', '07395', '07418', '07419', '07420', '07421', '07423', '07428', '07430', '07432', '07500', '13654', '13662', '13675', '13688', '13699', '13710', '13711', '13712', '13774', '13776', '13777', '14138', '14301', '15512', '15832', '15833', '15834', '15836', '15839', '15840', '15843', '15845', '19126', '19140', '19225', '19246', '19270', '19271', '19272', '19275', '19299', '19361', '19362']
all_gauges = ['00003','00020','00029','00044','00046','00047','00053','00071','00073','00078','00087','00091','00096','00103','00118','00124','00130','00131','00142','00146','00150','00151','00152','00154','00158','00161','00164','00167','00183','00191','00194','00198','00200','00205','00211','00213','00216','00217','00222','00227','00232','00240','00246','00257','00259','00269','00275','00279','00282','00287','00292','00294','00298','00301','00303','00310','00312','00314','00316','00320','00323','00326','00330','00336','00342','00348','00357','00359','00360','00377','00378','00379','00384','00389','00390','00399','00400','00403','00410','00420','00427','00430','00433','00443','00445','00450','00460','00468','00479','00498','00504','00505','00522','00523','00535','00542','00550','00551','00554','00555','00561','00567','00589','00591','00596','00599','00603','00604','00613','00617','00622','00630','00633','00644','00653','00656','00662','00677','00684','00685','00691','00701','00704','00714','00721','00723','00730','00731','00732','00735','00753','00755','00757','00760','00775','00789','00791','00796','00797','00801','00807','00808','00812','00814','00815','00817','00837','00839','00840','00848','00853','00856','00857','00863','00867','00871','00874','00880','00885','00891','00896','00902','00917','00921','00922','00931','00933','00934','00942','00953','00961','00962','00963','00966','00970','00974','00977','00978','00979','00983','00985','00988','00989','00991','01001','01014','01018','01023','01024','01030','01039','01046','01048','01050','01051','01052','01055','01056','01067','01072','01078','01089','01093','01094','01095','01103','01107','01119','01130','01132','01139','01158','01161','01166','01170','01176','01197','01200','01207','01210','01214','01216','01219','01223','01224','01237','01239','01241','01246','01253','01255','01262','01266','01270','01278','01279','01282','01290','01297','01300','01303','01304','01313','01315','01320','01327','01332','01336','01343','01346','01350','01357','01358','01366','01392','01411','01420','01424','01435','01441','01443','01451','01458','01468','01473','01495','01497','01503','01511','01526','01538','01542','01544','01550','01559','01561','01573','01578','01580','01584','01587','01590','01595','01598','01602','01605','01607','01612','01639','01642','01645','01650','01669','01684','01689','01691','01694','01711','01717','01721','01735','01736','01744','01750','01757','01759','01766','01769','01770','01792','01793','01801','01803','01810','01813','01814','01827','01830','01832','01844','01846','01847','01848','01851','01863','01869','01870','01886','01888','01900','01937','01938','01950','01957','01964','01975','01981','01997','02011','02012','02014','02023','02027','02039','02044','02050','02051','02064','02066','02072','02074','02080','02088','02109','02110','02115','02119','02152','02159','02167','02170','02171','02174','02175','02184','02201','02211','02213','02222','02233','02236','02252','02254','02261','02272','02274','02278','02290','02292','02293','02294','02306','02319','02323','02329','02331','02355','02362','02372','02376','02387','02388','02405','02409','02410','02412','02415','02416','02429','02431','02438','02444','02453','02465','02473','02480','02483','02485','02486','02497','02500','02503','02518','02522','02531','02532','02538','02541','02542','02546','02550','02556','02559','02562','02564','02575','02577','02578','02595','02597','02600','02601','02618','02619','02625','02627','02629','02638','02641','02660','02662','02667','02673','02677','02680','02689','02700','02703','02704','02708','02709','02712','02718','02733','02734','02740','02749','02750','02759','02763','02779','02787','02792','02794','02810','02812','02814','02822','02825','02839','02843','02844','02850','02856','02860','02878','02880','02884','02885','02890','02900','02907','02925','02928','02932','02947','02951','02953','02958','02968','02985','02988','02992','02996','02997','02999','03012','03015','03023','03024','03028','03031','03032','03034','03042','03044','03080','03081','03083','03086','03093','03094','03098','03121','03126','03136','03137','03146','03147','03148','03153','03155','03158','03164','03166','03167','03175','03179','03190','03192','03196','03204','03205','03207','03215','03217','03220','03226','03231','03234','03238','03244','03247','03248','03257','03258','03263','03268','03271','03272','03278','03279','03280','03284','03287','03289','03293','03297','03304','03307','03308','03319','03321','03339','03340','03342','03348','03362','03364','03366','03376','03379','03402','03413','03418','03426','03429','03432','03435','03438','03440','03442','03443','03445','03448','03473','03478','03485','03490','03491','03497','03499','03509','03513','03519','03525','03527','03535','03536','03538','03540','03545','03552','03558','03560','03564','03571','03572','03584','03589','03591','03602','03607','03612','03616','03617','03621','03625','03631','03650','03660','03667','03668','03677','03679','03681','03690','03700','03704','03714','03722','03729','03730','03733','03734','03739','03740','03761','03791','03795','03802','03811','03815','03820','03821','03836','03844','03848','03849','03853','03857','03875','03881','03886','03897','03904','03906','03911','03913','03919','03925','03927','03939','03945','03946','03948','03950','03960','03965','03967','03969','03972','03975','03987','03999','04000','04016','04017','04023','04024','04026','04032','04036','04039','04052','04063','04065','04078','04080','04090','04094','04101','04104','04109','04112','04127','04132','04134','04135','04150','04154','04159','04160','04167','04169','04175','04177','04185','04189','04211','04218','04219','04224','04230','04248','04251','04261','04271','04275','04280','04282','04287','04288','04290','04294','04300','04301','04303','04308','04310','04313','04315','04323','04336','04349','04351','04352','04354','04367','04368','04371','04374','04377','04387','04393','04400','04405','04411','04412','04413','04441','04445','04464','04466','04469','04480','04485','04488','04490','04493','04494','04501','04508','04546','04548','04555','04559','04560','04566','04567','04579','04592','04594','04599','04600','04601','04602','04603','04605','04617','04618','04623','04625','04637','04641','04642','04650','04651','04655','04666','04672','04683','04692','04694','04703','04704','04706','04709','04710','04712','04719','04741','04745','04748','04752','04755','04760','04763','04790','04801','04803','04816','04818','04827','04841','04849','04850','04857','04858','04878','04881','04883','04887','04896','04911','04912','04920','04926','04928','04931','04946','04958','04978','04982','04984','04997','05000','05002','05009','05013','05014','05017','05023','05029','05034','05036','05046','05047','05055','05057','05058','05059','05064','05084','05086','05097','05099','05100','05103','05109','05111','05123','05132','05133','05142','05146','05148','05149','05155','05158','05161','05162','05169','05171','05174','05187','05206','05209','05225','05227','05229','05230','05240','05262','05263','05275','05276','05277','05279','05280','05285','05294','05297','05300','05303','05335','05347','05349','05360','05371','05374','05382','05395','05397','05401','05404','05405','05416','05419','05424','05426','05433','05435','05440','05444','05453','05468','05470','05480','05484','05490','05501','05508','05511','05513','05516','05518','05524','05538','05541','05542','05546','05548','05555','05559','05562','05573','05600','05614','05616','05619','05625','05629','05635','05643','05646','05663','05664','05676','05678','05684','05688','05692','05699','05705','05711','05717','05719','05721','05724','05729','05731','05732','05733','05745','05750','05758','05762','05763','05767','05779','05793','05797','05800','05814','05822','05825','05839','05840','05854','05856','05871','05906','05930','05941','05943','05985','05986','05987','05988','05989','05990','05991','05992','05993','05994','06041','06042','06043','06044','06045','06046','06047','06048','06049','06050','06051','06052','06053','06058','06060','06061','06064','06067','06093','06100','06105','06109','06129','06157','06158','06159','06161','06163','06169','06170','06182','06186','06190','06191','06195','06197','06199','06200','06201','06203','06215','06216','06217','06242','06243','06244','06245','06246','06247','06249','06252','06255','06256','06257','06258','06259','06260','06262','06263','06264','06265','06266','06268','06269','06270','06271','06272','06273','06275','06276','06279','06280','06281','06282','06283','06284','06285','06286','06287','06288','06290','06293','06294','06295','06296','06297','06298','06299','06300','06301','06303','06305','06307','06310','06312','06313','06314','06315','06316','06317','06318','06319','06320','06321','06322','06323','06324','06325','06326','06327','06328','06329','06330','06331','06332','06333','06334','06336','06337','06338','06340','06341','06342','06343','06344','06346','06347','07075','07077','07078','07079','07099','07104','07105','07106','07135','07138','07139','07140','07187','07224','07226','07227','07228','07229','07230','07231','07233','07234','07235','07237','07238','07239','07240','07241','07242','07243','07244','07285','07287','07298','07319','07321','07322','07323','07324','07325','07326','07327','07328','07329','07330','07331','07333','07334','07335','07337','07341','07343','07344','07350','07351','07361','07364','07367','07368','07369','07370','07372','07373','07374','07375','07378','07380','07382','07389','07393','07394','07395','07396','07403','07410','07412','07418','07419','07420','07421','07423','07424','07425','07427','07428','07429','07430','07431','07432','07433','07434','07436','07487','07488','07489','07490','07491','07492','07493','07494','07495','07496','07497','07498','07499','07500','13654','13662','13669','13670','13671','13672','13674','13675','13687','13688','13689','13694','13695','13696','13698','13699','13700','13710','13711','13712','13713','13715','13716','13774','13776','13777','13778','13779','13780','13912','13918','13965','13968','14006','14007','14008','14009','14010','14011','14013','14014','14015','14016','14017','14018','14019','14020','14021','14022','14023','14024','14025','14026','14027','14028','14029','14030','14031','14032','14033','14034','14035','14036','14037','14038','14042','14052','14063','14065','14072','14108','14109','14138','14139','14142','14143','14144','14145','14146','14147','14148','14149','14150','14151','14152','14153','14154','14155','14156','14157','14158','14159','14164','14165','14166','14167','14168','14169','14170','14171','14172','14173','14174','14175','14176','14177','14178','14179','14180','14181','14182','14183','14184','14185','14186','14187','14301','14350','14351','15000','15003','15009','15011','15012','15013','15014','15015','15016','15039','15040','15045','15155','15156','15161','15170','15185','15187','15198','15201','15207','15212','15249','15444','15448','15478','15490','15512','15514','15517','15523','15555','15561','15569','15570','15810','15822','15831','15832','15834','15835','15838','15839','15840','15842','15843','15845','15850','15851','15930','15958','15986','15988','15989','19100']

if minutes == 60:
    gaugedata = read_gauges_60min(all_gauges, xgrid, ygrid)
if minutes == 5:
    gaugedata = read_gauges_1min(all_gauges, xgrid, ygrid, path_1min, minutes)

gauge_array, gauge_indices, gauge_array_ipol, gauge_stations = gaugearray(gaugedata, xgrid, ygrid)

# Plot composite.
plot_grid(radar, gaugedata, xgrid, ygrid, plottitle='09-01-2019 12:00 UTC\nDWD RADAR composite\nUTM zone 33N (EPSG 32633)', 
          filename=f"composite_{filename_drs[15:25]}_utm", minutes=minutes, plotgauges=False)

# Radar and obs coords as 2D-array.
radar_coords = wrl.util.gridaspoints(ygrid, xgrid)
obs_coords = zip(gaugedata["easting"], gaugedata["northing"])
obs_coords = np.array([list(elem) for elem in obs_coords])

# Apply adjustment methods.
if minutes == 60:
    minval = 0.1
if minutes == 5:
    minval = 0.01
adjuster = wrl.adjust.AdjustAdd(obs_coords, radar_coords, minval=0)
adjusted_add = adjuster(np.array(gaugedata["prec_mm"]), radar.reshape([700*700]))
adjuster = wrl.adjust.AdjustMultiply(obs_coords, radar_coords, minval=minval)
adjusted_mul = adjuster(np.array(gaugedata["prec_mm"]), radar.reshape([700*700])) 
adjuster = wrl.adjust.AdjustMFB(obs_coords, radar_coords)
adjusted_mulcon = adjuster(np.array(gaugedata["prec_mm"]), radar.reshape([700*700]))
adjuster = wrl.adjust.AdjustMixed(obs_coords, radar_coords)
adjusted_mix = adjuster(np.array(gaugedata["prec_mm"]), radar.reshape([700*700]))

# Reproject 1D-array (700*700 elements) to 2D-array (700,700).
gridshape = len(xgrid), len(ygrid)
adjusted_add_arr = adjusted_add.reshape(gridshape)
adjusted_mul_arr = adjusted_mul.reshape(gridshape)
adjusted_mulcon_arr = adjusted_mulcon.reshape(gridshape)
adjusted_mix_arr = adjusted_mix.reshape(gridshape)

# Correct bug in mixed adjustment.
adjusted_mix_arr[413:457, 269:310] = np.nan_to_num(adjusted_mix_arr[413:457, 269:310])

# Create mask for CZ/PL: Read shp boundary and replace 1 with NaN.
boundary_mask = np. loadtxt("geodata/DEU_east_boundary.txt")
for row in range(700):
    for col in range(700):
        if boundary_mask[row][col] == 1:
            boundary_mask[row][col] = np.NaN

# Create array with raw data for CZ/PL.
def raw_in_cz(array_adjusted):
    for i in range(len(boundary_mask)):
        for j in range(len(boundary_mask[0])):
            b = boundary_mask[i][j]
            if np.isnan(b):
                array_adjusted[i][j] = radar[i][j]
    return array_adjusted

# Plot adjusted radar data.
plot_grid(raw_in_cz(adjusted_add_arr), gaugedata, xgrid, ygrid, "Additive adjustment\n(spatially variable)", f"adjustment/adjustment_add", minutes, plotgauges=True)
plot_grid(adjusted_mul_arr, gaugedata, xgrid, ygrid,"Multiplicative adjustment\n(spatially variable)", f"adjustment/adjustment_mul", minutes, plotgauges=True)
plot_grid(adjusted_mulcon_arr, gaugedata, xgrid, ygrid,"Multiplicative adjustment\n(spatially uniform)", f"adjustment/adjustment_mfb", minutes, plotgauges=True)
plot_grid(raw_in_cz(adjusted_mix_arr), gaugedata, xgrid, ygrid,"Additive-multiplicative-mixed adjustment\n(spatially variable)", f"adjustment/adjustment_mixed", minutes, plotgauges=True)

# Plot errors.    
plot_grid(adjusted_add_arr - radar, gaugedata, xgrid, ygrid,"Additiver Fehler\n(räumlich variabel)", "adjustment/adjustment_add_diff", minutes, plotgauges=True)
plot_grid(adjusted_mul_arr - radar, gaugedata, xgrid, ygrid,"Multiplikativer Fehler\n(räumlich variabel)", "adjustment/adjustment_mul_diff", minutes, plotgauges=True)
plot_grid(adjusted_mulcon_arr - radar, gaugedata, xgrid, ygrid,"Multiplikativer Fehler\n(räumlich konstant)", "adjustment/adjustment_mfb_diff", minutes, plotgauges=True)
plot_grid(adjusted_mix_arr - radar, gaugedata, xgrid, ygrid,"Additiv-multiplikativer Fehler\n(räumlich variabel)", "adjustment/adjustment_mixed_diff", minutes, plotgauges=True)    

# Calculate bias indices.
def err_metrics(gauge_indices, predict_array, actual_array):
    gauge_list, rad_list = [], []
    for i in range(len(gauge_indices)):
        x,y = gauge_indices[i]
        rad_list.append(predict_array[y][x])
        gauge_list.append(actual_array[x][y])
    metrics = wrl.verify.ErrorMetrics(np.array(gauge_list), np.array(rad_list))
    return metrics.all()

print("metrics Add. adjustment", err_metrics(gauge_indices, adjusted_add_arr, gauge_array))
print("metrics Mul. adjustment", err_metrics(gauge_indices, adjusted_mul_arr, gauge_array))
print("metrics Mul. (spatially uniform) adjustment", err_metrics(gauge_indices, adjusted_mulcon_arr, gauge_array))
print("metrics Mixed adjustment", err_metrics(gauge_indices, adjusted_mix_arr, gauge_array))
print("metrics without adjustment", err_metrics(gauge_indices, radar, gauge_array))

# Remove CZ/PL data.
radar_de = np.add(radar, boundary_mask).reshape([700*700])
add_de = np.add(adjusted_add_arr, boundary_mask).reshape([700*700])
mul_de = np.add(adjusted_mul_arr, boundary_mask).reshape([700*700])
mulcon_de = np.add(adjusted_mulcon_arr, boundary_mask).reshape([700*700])
mix_de = np.add(adjusted_mix_arr, boundary_mask).reshape([700*700])

# Access gauge data within Germany.
rad = np.add(adjusted_add_arr,boundary_mask)
gauge_list = []
for i in range(len(gauge_indices)):
    x,y = gauge_indices[i]
    rad_val = rad[y][x]
    if not np.isnan(rad_val):
        gauge_list.append(gauge_array[x][y])

# Calculate quaniltes.
q_add = quantiles_100(add_de)
q_mul = quantiles_100(mul_de)
q_mulcon = quantiles_100(mulcon_de)
q_mix = quantiles_100(mix_de)
q_gau = quantiles_100(gauge_list)
q_rad = quantiles_100(radar_de)

# Plot QQ.
fig, ax = plt.subplots()    
plt.plot([0,1.5], [0,1.5], linewidth=0.5, color="grey", ls="-", alpha=0.8)
plt.scatter(q_gau, q_rad, label="radar (raw)", s=7, marker='o', alpha=0.8, c="green")
plt.scatter(q_gau, q_add, label="Add. adjustment", s=7, marker='o', alpha=0.8, c="red")
plt.scatter(q_gau, q_mul, label="Mul. adjustment", s=7, marker='o', alpha=0.8, c="blue")
plt.scatter(q_gau, q_mulcon, label="MFB adjustment", s=7, marker='o', alpha=0.8, c="brown")
plt.scatter(q_gau, q_mix, label="Add.-mul. adjustment", s=7, marker='o', alpha=0.8, c="orange")
if minutes == 5:
    plt.xlim([0,0.3])
    plt.ylim([0,0.3])
if minutes == 60:    
    plt.xlim([0,1.5])
    plt.ylim([0,2.5])
plt.xlabel("gauge - quantiles [mm]")
plt.ylabel("radar-quantiles [mm]")
plt.legend(loc="upper right")
plt.savefig(f"images/eval/qq_{minutes}min", dpi=600, bbox_inches='tight', transparent=False)