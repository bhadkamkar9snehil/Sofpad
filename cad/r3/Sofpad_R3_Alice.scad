/*
 Sofpad R3: two Sofle RGB halves in an Alice-style tilted plan with a CENTRE trackpad.
 The trackpad (Azoteq TPS65-201A-S, 65 x 49 mm) sits between the thumb clusters, so either
 thumb reaches it. Battery and carrier PCB sit behind the pad on the removable service plate.
 Real geometry: PCB outline, key and mount positions come from the Sofle RGB KiCad file.
 Keycaps, battery, carrier and pad bodies are fit-check envelopes, not part models.
 Run check_design.py after every edit; it proves fit, clearance and connectivity.
 All dimensions in mm.
*/
include <sofle_rgb_geometry.scad>;
include <sofle_components.scad>;

part = "assembly";   // shell bottom retainer keys pcbs knobs battery carrier padface assembly
chk_a = "";  chk_b = "";   // used by check_design.py
$fn = 48;

// ----- Plan -----
ang = 12;              // Alice tilt of each half, degrees (backs lean toward centre)
g = 92;                // gap between the two half pivots at the front edge
margin = 11;           // PCB outline to outer wall
wall = 3.2;

// ----- Heights -----
top_z = 17.5;
skin_t = 1.8;
pcb_bottom_z = 9.0;
pcb_t = 1.6;
plate_t = 1.8;
under_top = top_z - skin_t;
pcb_top_z = pcb_bottom_z + pcb_t;
edge_r = 2.0;          // top edge radius, built from 5 steps

// ----- Centre trackpad: Azoteq TPS65-201A-S -----
pad_w = 65;  pad_h = 49;
ov_w = 69.5; ov_h = 53;  ov_t = 0.75;       // overlay recess
win_w = 66.0; win_h = 49.8;
ret_w = 73;  ret_h = 57;  ret_t = 2;
ret_sx = 34.5; ret_sy = 26.5;
pad_top_z = 13.25;                          // module top; verify with sample
pad_cx = 0;  pad_cy = 25;

// ----- Behind the pad: battery (lying) then carrier -----
bat_w = 52; bat_l = 36; bat_t = 8;  bat_y0 = 56;     // NOVA 603450: 50 x 34 x 6 plus margin
car_w = 46; car_l = 22; car_t = 1.6; car_z = 5.6;    // carrier envelope, underside height
usb_x = -6; sw_x = 8;
usb_w = 11; usb_h = 5.1; sw_w = 10; sw_h = 4.2; port_z = 8.8;

mx_hole = 14.25;
enc_hole = 7.5;
insert_d = 3.2; insert_depth = 3.2; screw_hole = 2.3;
oled_win_w = 27; oled_win_h = 13;

hy = board_h*cos(ang);
hx = g/2 - board_h*sin(ang);
y_rear = hy + margin;
car_y = y_rear - wall - 1.2 - car_l/2;       // carrier sits against the rear wall
bat_y = bat_y0 + bat_l/2;

module rr(w,h,r) { offset(r=r) offset(delta=-r) square([w,h],center=true); }

module right_frame() { translate([g/2,0,0]) rotate([0,0,ang]) children(); }
module half_pose(side) {
  if(side=="right") right_frame() children();
  else mirror([1,0,0]) right_frame() children();
}

module plan_core() {
  half_pose("right") polygon(board_outline);
  half_pose("left")  polygon(board_outline);
  polygon([[-g/2,0],[g/2,0],[hx,hy],[-hx,hy]]);
}
module plan(inset=0) { offset(delta=-inset) offset(r=margin) plan_core(); }

// Rounded top edge: nested columns so hole walls stay seamless (no coplanar stacking).
module outer() {
  linear_extrude(height=top_z-edge_r) plan();
  for(i=[1:5]) let(t=i*90/5)
    translate([0,0,top_z-edge_r]) linear_extrude(height=edge_r*sin(t)) plan(edge_r*(1-cos(t)));
}

// ----- Cutouts -----
module key_cuts() for(s=["left","right"]) half_pose(s) {
  for(k=key_positions) translate([k[0],k[1],under_top-0.15]) rotate([0,0,k[2]])
    linear_extrude(height=skin_t+edge_r+0.5) square([mx_hole,mx_hole],center=true);
  for(e=encoder_positions) translate([e[0],e[1],under_top-0.15])
    cylinder(d=enc_hole,h=skin_t+edge_r+0.5);
  translate([96.7-82.05,146.8-74.6,under_top-0.2]) linear_extrude(height=skin_t+edge_r+0.6) rr(oled_win_w,oled_win_h,2);
}
module pad_cuts() translate([pad_cx,pad_cy,0]) {
  translate([0,0,top_z-ov_t-0.15]) linear_extrude(height=ov_t+0.4) rr(ov_w,ov_h,2);
  translate([0,0,under_top-0.2]) linear_extrude(height=skin_t+0.45) rr(win_w,win_h,2);
}
module port_cuts() {
  translate([usb_x-usb_w/2,y_rear-7,port_z-usb_h/2]) cube([usb_w,8,usb_h]);
  translate([sw_x-sw_w/2,y_rear-7,port_z-sw_h/2]) cube([sw_w,8,sw_h]);
}

// ----- Bosses -----
module insert_boss(d,h) difference() { cylinder(d=d,h=h); translate([0,0,-0.1]) cylinder(d=insert_d,h=insert_depth+0.1); }
module pcb_bosses() for(s=["left","right"]) half_pose(s) for(h=board_mount_holes)
  translate([h[0],h[1],pcb_top_z]) insert_boss(7.4,under_top-pcb_top_z+0.5);
module pad_bosses() translate([pad_cx,pad_cy,0]) for(dx=[-ret_sx,ret_sx],dy=[-ret_sy,ret_sy])
  translate([dx,dy,pad_top_z]) insert_boss(7.5,under_top-pad_top_z+0.5);

// Plate screws sit in the ring between the bevelled PCB outline and the wall (local half frame).
o = 4.4;
function wp(side,p) = side=="right" ? [g/2,0]+[p[0]*cos(ang)-p[1]*sin(ang), p[0]*sin(ang)+p[1]*cos(ang)]
                                    : let(q=wp("right",p)) [-q[0],q[1]];
ring_pts = [[34.2,2.0],[80,8.4],[78,116.2],[115.7,112.0],[147.8,45],[147.8,95]];
screws = concat([for(s=["left","right"]) for(p=ring_pts) wp(s,p)], [[0,-o]]);
module plate_bosses() for(p=screws) translate([p[0],p[1],plate_t]) insert_boss(7,5);

// ----- Parts -----
module shell() {
  union() {
    difference() {
      outer();
      translate([0,0,-0.05]) linear_extrude(height=under_top+0.05) plan(wall);
      key_cuts(); pad_cuts(); port_cuts();
    }
    pcb_bosses(); pad_bosses(); plate_bosses();
  }
}
module bottom() {
  difference() {
    linear_extrude(height=plate_t) plan(wall+0.55);
    for(p=screws) translate([p[0],p[1],-0.1]) cylinder(d=screw_hole,h=plate_t+0.2);
  }
  for(dx=[-1,1],dy=[-1,1]) translate([dx*(bat_w/2+1.3),bat_y+dy*(bat_l/2+1.2),plate_t]) linear_extrude(height=2.2) rr(5,5,1);
  for(dx=[-car_w/2+4,car_w/2-4],dy=[-car_l/2+3,car_l/2-3]) translate([dx,car_y+dy,plate_t]) insert_boss(5,car_z-plate_t);
}
module retainer() {
  difference() {
    linear_extrude(height=ret_t) rr(ret_w,ret_h,4);
    translate([0,0,-0.1]) linear_extrude(height=ret_t+0.2) rr(pad_w-3,pad_h-3,1.5);
    for(dx=[-ret_sx,ret_sx],dy=[-ret_sy,ret_sy]) translate([dx,dy,-0.1]) cylinder(d=screw_hole,h=ret_t+0.2);
    translate([-6,ret_h/2-8,-0.1]) cube([12,12,ret_t+0.2]);   // FFC exit to the rear
  }
}

// ----- Envelopes (fit checks and renders) -----
module pcbs() for(s=["left","right"]) half_pose(s) translate([0,0,pcb_bottom_z]) linear_extrude(height=pcb_t) polygon(board_outline);
module keys() for(s=["left","right"]) half_pose(s) for(k=key_positions)
  translate([k[0],k[1],top_z+5]) rotate([0,0,k[2]]) linear_extrude(height=6.8,scale=0.91) rr(17.5,17.5,1);
module knobs() for(s=["left","right"]) half_pose(s) for(e=encoder_positions) translate([e[0],e[1],top_z+2.8]) cylinder(d=13,h=9);
module battery() translate([0,bat_y,plate_t+0.65+bat_t/2]) cube([bat_w,bat_l,bat_t],center=true);
module carrier() translate([0,car_y,car_z+car_t/2]) cube([car_w,car_l,car_t],center=true);
module padface() translate([pad_cx,pad_cy,top_z-ov_t+0.03]) linear_extrude(height=ov_t-0.2) rr(ov_w,ov_h,2);
module padbody() translate([pad_cx,pad_cy,pad_top_z-3]) linear_extrude(height=3) rr(pad_w,pad_h,2);
module retainer_placed() translate([pad_cx,pad_cy,pad_top_z-ret_t]) retainer();
module cavity() translate([0,0,plate_t]) linear_extrude(height=under_top-plate_t) plan(wall);
module usb_env() translate([usb_x,y_rear-wall-3,port_z]) cube([9,6,3.3],center=true);

module by_name(n) {
  if(n=="battery") battery(); else if(n=="carrier") carrier(); else if(n=="pcbs") pcbs();
  else if(n=="padbody") padbody(); else if(n=="retainer") retainer_placed(); else if(n=="cavity") cavity();
  else if(n=="bosses") { pcb_bosses(); pad_bosses(); } else if(n=="platebosses") plate_bosses();
  else if(n=="usb") usb_env();
}

if(part=="shell") shell();
else if(part=="bottom") bottom();
else if(part=="retainer") retainer();
else if(part=="keys") keys();
else if(part=="pcbs") pcbs();
else if(part=="knobs") knobs();
else if(part=="battery") battery();
else if(part=="carrier") carrier();
else if(part=="padface") padface();
else if(part=="overlap") intersection(){ by_name(chk_a); by_name(chk_b); }
else if(part=="outside") difference(){ by_name(chk_a); by_name(chk_b); }
else { shell(); translate([0,0,-0.1]) bottom(); pcbs(); keys(); knobs(); battery(); carrier(); padface(); translate([pad_cx,pad_cy,pad_top_z-ret_t]) retainer(); }
