function _bottom_case_walls_extrude_6_6_outline_fn(){
    return new CSG.Path2D([[89.867,-108.9975396],[89.865,-35.7275396]]).appendPoint([89.8649741,-34.7775393]).appendArc([90.3649606,-34.2775257],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([126.3650135,-34.2765527]).appendArc([126.865,-33.7765527],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([126.865,-30.1525]).appendArc([127.365,-29.6525],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([144.865,-29.6525]).appendArc([145.365,-29.1525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([145.365,-27.9595]).appendArc([145.865,-27.4595],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([165.293,-27.4595]).appendArc([165.793,-27.9595],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([165.793,-29.1525]).appendArc([166.293,-29.6525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([183.793,-29.6525]).appendArc([184.293,-30.1525],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([184.293,-31.5831581]).appendArc([184.7929595,-32.0831581],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([202.2941889,-32.0845771]).appendArc([202.7941479,-32.5851812],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([202.7929989,-33.5362518]).appendPoint([202.7703576,-52.276896]).appendArc([203.2703572,-52.7775],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([222.518,-52.7775]).appendArc([223.018,-53.2775],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([223.018,-113.4770263]).appendPoint([222.5120415,-114.3533721]).appendArc([222.5103586,-114.3563098],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([208.7519894,-138.5635762]).appendArc([208.0672938,-138.7495266],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([192.302732,-129.6478526]).appendArc([192.1176393,-129.5850962],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([155.45095,-124.7845997]).appendArc([155.1109704,-124.5822016],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([145.0172618,-110.6516749]).appendArc([144.6123519,-110.4450458],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([90.367049,-110.4475438]).appendArc([89.8670259,-109.9475575],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([89.867,-108.9975396]).close().innerToCAG()
.subtract(
    new CSG.Path2D([[91.067,-108.9975068],[91.065,-35.7275068]]).appendPoint([91.0649932,-35.4775068]).appendPoint([127.5650135,-35.4765203]).appendArc([128.065,-34.9765203],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([128.065,-30.8525]).appendPoint([146.065,-30.8525]).appendArc([146.565,-30.3525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([146.565,-28.6595]).appendPoint([164.593,-28.6595]).appendPoint([164.593,-30.3525]).appendArc([165.093,-30.8525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([183.093,-30.8525]).appendPoint([183.093,-32.7830608]).appendArc([183.5929595,-33.2830608],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([201.5933022,-33.2845203]).appendPoint([201.5929998,-33.534802]).appendPoint([201.568907,-53.476896]).appendArc([202.0689066,-53.9775],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([221.818,-53.9775]).appendPoint([221.818,-113.1554873]).appendPoint([221.4707761,-113.7568968]).appendArc([221.4690932,-113.7598345],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([208.0569573,-137.3579181]).appendPoint([207.8389799,-137.2320689]).appendPoint([192.6956285,-128.4890509]).appendArc([192.5105358,-128.4262945],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([155.905752,-123.6339028]).appendPoint([145.6296466,-109.4516467]).appendArc([145.2247366,-109.2450176],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([91.0670068,-109.2475115]).appendPoint([91.067,-108.9975068]).close().innerToCAG()
).extrude({ offset: [0, 0, 6.6] });
}


function _mcu_wall_cutout_extrude_2_2_outline_fn(){
    return new CSG.Path2D([[208.279,-82.1375],[216.279,-82.1375]]).appendPoint([216.279,-39.2375]).appendPoint([208.279,-39.2375]).appendPoint([208.279,-82.1375]).close().innerToCAG()
.extrude({ offset: [0, 0, 2.2] });
}


function _bottom_case_outer_outline_extrude_1_outline_fn(){
    return new CSG.Path2D([[89.867,-108.9975396],[89.865,-35.7275396]]).appendPoint([89.8649741,-34.7775393]).appendArc([90.3649606,-34.2775257],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([126.3650135,-34.2765527]).appendArc([126.865,-33.7765527],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([126.865,-30.1525]).appendArc([127.365,-29.6525],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([144.865,-29.6525]).appendArc([145.365,-29.1525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([145.365,-27.9595]).appendArc([145.865,-27.4595],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([165.293,-27.4595]).appendArc([165.793,-27.9595],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([165.793,-29.1525]).appendArc([166.293,-29.6525],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([183.793,-29.6525]).appendArc([184.293,-30.1525],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([184.293,-31.5831581]).appendArc([184.7929595,-32.0831581],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([202.2941889,-32.0845771]).appendArc([202.7941479,-32.5851812],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([202.7929989,-33.5362518]).appendPoint([202.7703576,-52.276896]).appendArc([203.2703572,-52.7775],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([222.518,-52.7775]).appendArc([223.018,-53.2775],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([223.018,-113.4770263]).appendPoint([222.5120415,-114.3533721]).appendArc([222.5103586,-114.3563098],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([208.7519894,-138.5635762]).appendArc([208.0672938,-138.7495266],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([192.302732,-129.6478526]).appendArc([192.1176393,-129.5850962],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([155.45095,-124.7845997]).appendArc([155.1109704,-124.5822016],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([145.0172618,-110.6516749]).appendArc([144.6123519,-110.4450458],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([90.367049,-110.4475438]).appendArc([89.8670259,-109.9475575],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([89.867,-108.9975396]).close().innerToCAG()
.extrude({ offset: [0, 0, 1] });
}


function _screws_extrude_1_outline_fn(){
    return CAG.circle({"center":[196.7245951,-115.0067481],"radius":1.1})
.union(
    CAG.circle({"center":[151.157,-107.615],"radius":1.1})
).union(
    CAG.circle({"center":[183.218,-50.2985],"radius":1.1})
).union(
    CAG.circle({"center":[109.25,-90.75],"radius":1.1})
).union(
    CAG.circle({"center":[109.25,-53.75],"radius":1.1})
).extrude({ offset: [0, 0, 1] });
}




                function knucles_bottom_tray_case_fn() {
                    

                // creating part 0 of case knucles_bottom_tray
                let knucles_bottom_tray__part_0 = _bottom_case_walls_extrude_6_6_outline_fn();

                // make sure that rotations are relative
                let knucles_bottom_tray__part_0_bounds = knucles_bottom_tray__part_0.getBounds();
                let knucles_bottom_tray__part_0_x = knucles_bottom_tray__part_0_bounds[0].x + (knucles_bottom_tray__part_0_bounds[1].x - knucles_bottom_tray__part_0_bounds[0].x) / 2
                let knucles_bottom_tray__part_0_y = knucles_bottom_tray__part_0_bounds[0].y + (knucles_bottom_tray__part_0_bounds[1].y - knucles_bottom_tray__part_0_bounds[0].y) / 2
                knucles_bottom_tray__part_0 = translate([-knucles_bottom_tray__part_0_x, -knucles_bottom_tray__part_0_y, 0], knucles_bottom_tray__part_0);
                knucles_bottom_tray__part_0 = rotate([0,0,0], knucles_bottom_tray__part_0);
                knucles_bottom_tray__part_0 = translate([knucles_bottom_tray__part_0_x, knucles_bottom_tray__part_0_y, 0], knucles_bottom_tray__part_0);

                knucles_bottom_tray__part_0 = translate([-75,0,0], knucles_bottom_tray__part_0);
                let result = knucles_bottom_tray__part_0;
                
            

                // creating part 1 of case knucles_bottom_tray
                let knucles_bottom_tray__part_1 = _mcu_wall_cutout_extrude_2_2_outline_fn();

                // make sure that rotations are relative
                let knucles_bottom_tray__part_1_bounds = knucles_bottom_tray__part_1.getBounds();
                let knucles_bottom_tray__part_1_x = knucles_bottom_tray__part_1_bounds[0].x + (knucles_bottom_tray__part_1_bounds[1].x - knucles_bottom_tray__part_1_bounds[0].x) / 2
                let knucles_bottom_tray__part_1_y = knucles_bottom_tray__part_1_bounds[0].y + (knucles_bottom_tray__part_1_bounds[1].y - knucles_bottom_tray__part_1_bounds[0].y) / 2
                knucles_bottom_tray__part_1 = translate([-knucles_bottom_tray__part_1_x, -knucles_bottom_tray__part_1_y, 0], knucles_bottom_tray__part_1);
                knucles_bottom_tray__part_1 = rotate([0,0,0], knucles_bottom_tray__part_1);
                knucles_bottom_tray__part_1 = translate([knucles_bottom_tray__part_1_x, knucles_bottom_tray__part_1_y, 0], knucles_bottom_tray__part_1);

                knucles_bottom_tray__part_1 = translate([-75,0,1], knucles_bottom_tray__part_1);
                result = result.subtract(knucles_bottom_tray__part_1);
                
            

                // creating part 2 of case knucles_bottom_tray
                let knucles_bottom_tray__part_2 = _bottom_case_outer_outline_extrude_1_outline_fn();

                // make sure that rotations are relative
                let knucles_bottom_tray__part_2_bounds = knucles_bottom_tray__part_2.getBounds();
                let knucles_bottom_tray__part_2_x = knucles_bottom_tray__part_2_bounds[0].x + (knucles_bottom_tray__part_2_bounds[1].x - knucles_bottom_tray__part_2_bounds[0].x) / 2
                let knucles_bottom_tray__part_2_y = knucles_bottom_tray__part_2_bounds[0].y + (knucles_bottom_tray__part_2_bounds[1].y - knucles_bottom_tray__part_2_bounds[0].y) / 2
                knucles_bottom_tray__part_2 = translate([-knucles_bottom_tray__part_2_x, -knucles_bottom_tray__part_2_y, 0], knucles_bottom_tray__part_2);
                knucles_bottom_tray__part_2 = rotate([0,0,0], knucles_bottom_tray__part_2);
                knucles_bottom_tray__part_2 = translate([knucles_bottom_tray__part_2_x, knucles_bottom_tray__part_2_y, 0], knucles_bottom_tray__part_2);

                knucles_bottom_tray__part_2 = translate([-75,0,0], knucles_bottom_tray__part_2);
                result = result.union(knucles_bottom_tray__part_2);
                
            

                // creating part 3 of case knucles_bottom_tray
                let knucles_bottom_tray__part_3 = _screws_extrude_1_outline_fn();

                // make sure that rotations are relative
                let knucles_bottom_tray__part_3_bounds = knucles_bottom_tray__part_3.getBounds();
                let knucles_bottom_tray__part_3_x = knucles_bottom_tray__part_3_bounds[0].x + (knucles_bottom_tray__part_3_bounds[1].x - knucles_bottom_tray__part_3_bounds[0].x) / 2
                let knucles_bottom_tray__part_3_y = knucles_bottom_tray__part_3_bounds[0].y + (knucles_bottom_tray__part_3_bounds[1].y - knucles_bottom_tray__part_3_bounds[0].y) / 2
                knucles_bottom_tray__part_3 = translate([-knucles_bottom_tray__part_3_x, -knucles_bottom_tray__part_3_y, 0], knucles_bottom_tray__part_3);
                knucles_bottom_tray__part_3 = rotate([0,0,0], knucles_bottom_tray__part_3);
                knucles_bottom_tray__part_3 = translate([knucles_bottom_tray__part_3_x, knucles_bottom_tray__part_3_y, 0], knucles_bottom_tray__part_3);

                knucles_bottom_tray__part_3 = translate([-75,0,0], knucles_bottom_tray__part_3);
                result = result.subtract(knucles_bottom_tray__part_3);
                
            
                    return result;
                }
            
            
        
            function main() {
                return knucles_bottom_tray_case_fn();
            }

        