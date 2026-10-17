function _bottom_case_walls_extrude_6_6_outline_fn(){
    return new CSG.Path2D([[89.397,-109.4825376],[89.395,-32.2525376]]).appendPoint([89.3949754,-31.3025373]).appendArc([89.8949626,-30.8025244],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([127.8950128,-30.80155]).appendArc([128.395,-30.30155],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([128.395,-26.4275]).appendArc([128.895,-25.9275],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([147.395,-25.9275]).appendArc([147.895,-25.4275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([147.895,-24.1165]).appendArc([148.395,-23.6165],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([168.771,-23.6165]).appendArc([169.271,-24.1165],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([169.271,-25.4275]).appendArc([169.771,-25.9275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([188.271,-25.9275]).appendArc([188.771,-26.4275],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([188.771,-27.99285]).appendArc([189.2710384,-28.49285],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([207.7697862,-28.491427]).appendArc([208.2698242,-28.9908081],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([208.2709989,-29.939705]).appendPoint([208.295588,-49.803119]).appendArc([208.7955876,-50.3025],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([229.048,-50.3025]).appendArc([229.548,-50.8025],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([229.548,-114.2020263]).appendPoint([229.0387368,-115.084096]).appendPoint([229.0364302,-115.0880912]).appendPoint([229.0340982,-115.0920716]).appendPoint([214.2570168,-140.3147114]).appendArc([213.5756036,-140.4949739],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([196.9957745,-130.9226051]).appendArc([196.8101294,-130.8597766],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([158.4848573,-125.8855677]).appendArc([158.1459009,-125.6852597],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([147.4871887,-111.1394235]).appendArc([147.0838993,-110.9349568],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([89.8970027,-110.9324585]).appendArc([89.3970246,-110.4324714],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([89.397,-109.4825376]).close().innerToCAG()
.subtract(
    new CSG.Path2D([[90.597,-109.4825065],[90.595,-32.2525065]]).appendPoint([90.5949935,-32.0025064]).appendPoint([129.0950128,-32.0015192]).appendArc([129.595,-31.5015192],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([129.595,-27.1275]).appendPoint([148.595,-27.1275]).appendArc([149.095,-26.6275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([149.095,-24.8165]).appendPoint([168.071,-24.8165]).appendPoint([168.071,-26.6275]).appendArc([168.571,-27.1275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([187.571,-27.1275]).appendPoint([187.571,-29.1929423]).appendArc([188.0710384,-29.6929423],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([207.0706907,-29.6914808]).appendPoint([207.0709998,-29.9411905]).appendPoint([207.0970725,-51.003119]).appendArc([207.5970721,-51.5025],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([228.348,-51.5025]).appendPoint([228.348,-113.8804873]).appendPoint([227.9995064,-114.484096]).appendPoint([213.5732311,-139.1079635]).appendPoint([197.3880687,-129.7634557]).appendArc([197.2024236,-129.7006272],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([158.9366348,-124.7341385]).appendPoint([148.0955718,-109.9394501]).appendArc([147.6922823,-109.7349834],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([90.5970065,-109.7324891]).appendPoint([90.597,-109.4825065]).close().innerToCAG()
).extrude({ offset: [0, 0, 6.6] });
}


function _mcu_wall_cutout_extrude_2_2_outline_fn(){
    return new CSG.Path2D([[213.279,-80.0125],[221.279,-80.0125]]).appendPoint([221.279,-37.1125]).appendPoint([213.279,-37.1125]).appendPoint([213.279,-80.0125]).close().innerToCAG()
.extrude({ offset: [0, 0, 2.2] });
}


function _bottom_case_outer_outline_extrude_1_outline_fn(){
    return new CSG.Path2D([[89.397,-109.4825376],[89.395,-32.2525376]]).appendPoint([89.3949754,-31.3025373]).appendArc([89.8949626,-30.8025244],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([127.8950128,-30.80155]).appendArc([128.395,-30.30155],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([128.395,-26.4275]).appendArc([128.895,-25.9275],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([147.395,-25.9275]).appendArc([147.895,-25.4275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([147.895,-24.1165]).appendArc([148.395,-23.6165],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([168.771,-23.6165]).appendArc([169.271,-24.1165],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([169.271,-25.4275]).appendArc([169.771,-25.9275],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([188.271,-25.9275]).appendArc([188.771,-26.4275],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([188.771,-27.99285]).appendArc([189.2710384,-28.49285],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([207.7697862,-28.491427]).appendArc([208.2698242,-28.9908081],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([208.2709989,-29.939705]).appendPoint([208.295588,-49.803119]).appendArc([208.7955876,-50.3025],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([229.048,-50.3025]).appendArc([229.548,-50.8025],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([229.548,-114.2020263]).appendPoint([229.0387368,-115.084096]).appendPoint([229.0364302,-115.0880912]).appendPoint([229.0340982,-115.0920716]).appendPoint([214.2570168,-140.3147114]).appendArc([213.5756036,-140.4949739],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([196.9957745,-130.9226051]).appendArc([196.8101294,-130.8597766],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([158.4848573,-125.8855677]).appendArc([158.1459009,-125.6852597],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([147.4871887,-111.1394235]).appendArc([147.0838993,-110.9349568],{"radius":0.5,"clockwise":false,"large":false}).appendPoint([89.8970027,-110.9324585]).appendArc([89.3970246,-110.4324714],{"radius":0.5,"clockwise":true,"large":false}).appendPoint([89.397,-109.4825376]).close().innerToCAG()
.extrude({ offset: [0, 0, 1] });
}


function _screws_extrude_1_outline_fn(){
    return CAG.circle({"center":[201.7575083,-115.6405671],"radius":1.1})
.union(
    CAG.circle({"center":[154.157,-107.865],"radius":1.1})
).union(
    CAG.circle({"center":[187.718,-47.6735],"radius":1.1})
).union(
    CAG.circle({"center":[109.75,-90.25],"radius":1.1})
).union(
    CAG.circle({"center":[109.75,-51.25],"radius":1.1})
).extrude({ offset: [0, 0, 1] });
}




                function knuckles_bottom_tray_case_fn() {
                    

                // creating part 0 of case knuckles_bottom_tray
                let knuckles_bottom_tray__part_0 = _bottom_case_walls_extrude_6_6_outline_fn();

                // make sure that rotations are relative
                let knuckles_bottom_tray__part_0_bounds = knuckles_bottom_tray__part_0.getBounds();
                let knuckles_bottom_tray__part_0_x = knuckles_bottom_tray__part_0_bounds[0].x + (knuckles_bottom_tray__part_0_bounds[1].x - knuckles_bottom_tray__part_0_bounds[0].x) / 2
                let knuckles_bottom_tray__part_0_y = knuckles_bottom_tray__part_0_bounds[0].y + (knuckles_bottom_tray__part_0_bounds[1].y - knuckles_bottom_tray__part_0_bounds[0].y) / 2
                knuckles_bottom_tray__part_0 = translate([-knuckles_bottom_tray__part_0_x, -knuckles_bottom_tray__part_0_y, 0], knuckles_bottom_tray__part_0);
                knuckles_bottom_tray__part_0 = rotate([0,0,0], knuckles_bottom_tray__part_0);
                knuckles_bottom_tray__part_0 = translate([knuckles_bottom_tray__part_0_x, knuckles_bottom_tray__part_0_y, 0], knuckles_bottom_tray__part_0);

                knuckles_bottom_tray__part_0 = translate([-75,0,0], knuckles_bottom_tray__part_0);
                let result = knuckles_bottom_tray__part_0;
                
            

                // creating part 1 of case knuckles_bottom_tray
                let knuckles_bottom_tray__part_1 = _mcu_wall_cutout_extrude_2_2_outline_fn();

                // make sure that rotations are relative
                let knuckles_bottom_tray__part_1_bounds = knuckles_bottom_tray__part_1.getBounds();
                let knuckles_bottom_tray__part_1_x = knuckles_bottom_tray__part_1_bounds[0].x + (knuckles_bottom_tray__part_1_bounds[1].x - knuckles_bottom_tray__part_1_bounds[0].x) / 2
                let knuckles_bottom_tray__part_1_y = knuckles_bottom_tray__part_1_bounds[0].y + (knuckles_bottom_tray__part_1_bounds[1].y - knuckles_bottom_tray__part_1_bounds[0].y) / 2
                knuckles_bottom_tray__part_1 = translate([-knuckles_bottom_tray__part_1_x, -knuckles_bottom_tray__part_1_y, 0], knuckles_bottom_tray__part_1);
                knuckles_bottom_tray__part_1 = rotate([0,0,0], knuckles_bottom_tray__part_1);
                knuckles_bottom_tray__part_1 = translate([knuckles_bottom_tray__part_1_x, knuckles_bottom_tray__part_1_y, 0], knuckles_bottom_tray__part_1);

                knuckles_bottom_tray__part_1 = translate([-75,0,1], knuckles_bottom_tray__part_1);
                result = result.subtract(knuckles_bottom_tray__part_1);
                
            

                // creating part 2 of case knuckles_bottom_tray
                let knuckles_bottom_tray__part_2 = _bottom_case_outer_outline_extrude_1_outline_fn();

                // make sure that rotations are relative
                let knuckles_bottom_tray__part_2_bounds = knuckles_bottom_tray__part_2.getBounds();
                let knuckles_bottom_tray__part_2_x = knuckles_bottom_tray__part_2_bounds[0].x + (knuckles_bottom_tray__part_2_bounds[1].x - knuckles_bottom_tray__part_2_bounds[0].x) / 2
                let knuckles_bottom_tray__part_2_y = knuckles_bottom_tray__part_2_bounds[0].y + (knuckles_bottom_tray__part_2_bounds[1].y - knuckles_bottom_tray__part_2_bounds[0].y) / 2
                knuckles_bottom_tray__part_2 = translate([-knuckles_bottom_tray__part_2_x, -knuckles_bottom_tray__part_2_y, 0], knuckles_bottom_tray__part_2);
                knuckles_bottom_tray__part_2 = rotate([0,0,0], knuckles_bottom_tray__part_2);
                knuckles_bottom_tray__part_2 = translate([knuckles_bottom_tray__part_2_x, knuckles_bottom_tray__part_2_y, 0], knuckles_bottom_tray__part_2);

                knuckles_bottom_tray__part_2 = translate([-75,0,0], knuckles_bottom_tray__part_2);
                result = result.union(knuckles_bottom_tray__part_2);
                
            

                // creating part 3 of case knuckles_bottom_tray
                let knuckles_bottom_tray__part_3 = _screws_extrude_1_outline_fn();

                // make sure that rotations are relative
                let knuckles_bottom_tray__part_3_bounds = knuckles_bottom_tray__part_3.getBounds();
                let knuckles_bottom_tray__part_3_x = knuckles_bottom_tray__part_3_bounds[0].x + (knuckles_bottom_tray__part_3_bounds[1].x - knuckles_bottom_tray__part_3_bounds[0].x) / 2
                let knuckles_bottom_tray__part_3_y = knuckles_bottom_tray__part_3_bounds[0].y + (knuckles_bottom_tray__part_3_bounds[1].y - knuckles_bottom_tray__part_3_bounds[0].y) / 2
                knuckles_bottom_tray__part_3 = translate([-knuckles_bottom_tray__part_3_x, -knuckles_bottom_tray__part_3_y, 0], knuckles_bottom_tray__part_3);
                knuckles_bottom_tray__part_3 = rotate([0,0,0], knuckles_bottom_tray__part_3);
                knuckles_bottom_tray__part_3 = translate([knuckles_bottom_tray__part_3_x, knuckles_bottom_tray__part_3_y, 0], knuckles_bottom_tray__part_3);

                knuckles_bottom_tray__part_3 = translate([-75,0,0], knuckles_bottom_tray__part_3);
                result = result.subtract(knuckles_bottom_tray__part_3);
                
            
                    return result;
                }
            
            
        
            function main() {
                return knuckles_bottom_tray_case_fn();
            }

        