/*
 Sofpad R3: two Sofle RGB halves in an Alice-style tented plan, TPS65 trackpad on the right.
 One top shell, one removable service plate. Battery and carrier PCB live on the plate.
 Real geometry: PCB outline, key and mount positions come from the Sofle RGB KiCad file.
 Keycaps, battery, carrier and trackpad bodies are envelopes for fit checks, not part models.
 All dimensions in mm. Export parts with -D 'part="shell"' etc.
*/
include <sofle_rgb_geometry.scad>;
include <sofle_components.scad>;

part = "assembly";   // shell bottom retainer | assembly keys pcbs knobs battery carrier padface
$fn = 48;

// ----- Plan -----
ang = 12;              // Alice tilt of each half, degrees (backs lean toward centre)
g = 76;                // gap between the two half pivots at the front edge
margin = 11;           // beyond PCB outline to outer wall
wall = 3.2;
pad_gapx = 2;          // PCB edge to retainer edge

// ----- Heights -----
top_z = 17.5;
skin_t = 1.8;
pcb_bottom_z = 9.0;
pcb_t = 1.6;
plate_t = 1.8;
under_top = top_z - skin_t;
pcb_top_z = pcb_bottom_z + pcb_t;

// ----- Trackpad: Azoteq TPS65-201A-S, 65 x 49 mm -----
pad_w = 65;  pad_h = 49;
ov_w = 69.5; ov_h = 53;  ov_t = 0.75;       // overlay recess (module + 4.5)
win_w = 66.0; win_h = 49.8;
ret_w = 81;  ret_h = 63;  ret_t = 2;
ret_sx = 37.5; ret_sy = 28.5;               // retainer screw offsets
pad_top_z = 13.25;                          // module top; verify with sample
pad_lx = board_w + pad_gapx + ret_w/2;
pad_ly = board_h/2;

// ----- Centre bay (battery front, carrier rear) -----
bat_w = 36; bat_l = 52; bat_t = 8;  bat_y = 4;
car_w = 24; car_l = 52; car_t = 1.6; car_z = 5.6;   // carrier PCB underside height
usb_x = -5; sw_x = 6.5;
usb_w = 11; usb_h = 5.1; sw_w = 10; sw_h = 4.2; port_z = 8.8;

mx_hole = 14.25;
enc_hole = 7.5;
insert_d = 3.2; insert_depth = 3.2; screw_hole = 2.3;
oled_win_w = 27; oled_win_h = 13;

hy = board_h*cos(ang);
hx = g/2 - board_h*sin(ang);        // half-gap at the rear inner corners
y_rear = hy + margin;
car_y = y_rear - 7 - car_l/2;

module rr(w,h,r) { offset(r=r) offset(delta=-r) square([w,h],center=true); }

// Right half frame (pivot at front, tilted); left half is its mirror.
module right_frame() { translate([g/2,0,0]) rotate([0,0,ang]) children(); }
module half_pose(side) {
  if(side=="right") right_frame() children();
  else mirror([1,0,0]) right_frame() children();
}
module pad_pose() { right_frame() translate([pad_lx,pad_ly,0]) children(); }

module plan_core() {
  half_pose("right") polygon(board_outline);
  half_pose("left")  polygon(board_outline);
  polygon([[-g/2,0],[g/2,0],[hx,hy],[-hx,hy]]);
  right_frame() translate([board_w-6,pad_ly-ret_h/2]) square([ret_w+pad_gapx+6,ret_h]);
}
module plan(inset=0) { offset(delta=-inset) offset(r=margin) plan_core(); }

module outer() {
  linear_extrude(height=top_z-1.2) plan();
  for(i=[0:2]) translate([0,0,top_z-1.2+i*0.4]) linear_extrude(height=0.4) plan(0.4*(i+1));
}

// ----- Cutouts -----
module key_cuts() for(s=["left","right"]) half_pose(s) {
  for(k=key_positions) translate([k[0],k[1],under_top-0.15]) rotate([0,0,k[2]])
    linear_extrude(height=skin_t+0.5) square([mx_hole,mx_hole],center=true);
  for(e=encoder_positions) translate([e[0],e[1],under_top-0.15])
    cylinder(d=enc_hole,h=skin_t+0.5);
  translate([96.7-82.05,146.8-74.6,under_top-0.2]) linear_extrude(height=skin_t+0.6) rr(oled_win_w,oled_win_h,2);
}
module pad_cuts() pad_pose() {
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
module pad_bosses() pad_pose() for(dx=[-ret_sx,ret_sx],dy=[-ret_sy,ret_sy])
  translate([dx,dy,pad_top_z]) insert_boss(7.5,under_top-pad_top_z+0.5);

// Plate screw points: in the ring between PCB edge and wall.
o = 4.4;
plate_pts = concat(
  [for(s=["left"]) each [[board_w+o,-o],[board_w+o,board_h+o],[board_w/2,-o],[board_w/2,board_h+o]]],
  [[0,0]]);
function wp(side,p) = side=="right" ? [g/2,0]+[p[0]*cos(ang)-p[1]*sin(ang), p[0]*sin(ang)+p[1]*cos(ang)]
                                    : let(q=wp("right",p)) [-q[0],q[1]];
screws = concat(
  [for(p=[[board_w+o,-o],[board_w+o,board_h+o],[board_w/2,-o],[board_w/2,board_h+o]]) wp("left",p)],
  [for(p=[[board_w/2,-o],[board_w/2,board_h+o]]) wp("right",p)],
  [for(sy=[-1,1]) wp("right",[pad_lx+ret_w/2+o,pad_ly+sy*(ret_h/2+o)])],
  [[0,-o]]);
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
  // battery tray lips and carrier standoffs ride on the plate
  for(dx=[-1,1],dy=[-1,1]) translate([dx*(bat_w/2+1.3),bat_y+bat_l/2+dy*(bat_l/2+1.2),plate_t]) linear_extrude(height=2.2) rr(5,5,1);
  for(dx=[-8.5,8.5],dy=[-22,22]) translate([dx,car_y+dy,plate_t]) insert_boss(5,car_z-plate_t);
}
module retainer() {
  difference() {
    linear_extrude(height=ret_t) rr(ret_w,ret_h,4);
    translate([0,0,-0.1]) linear_extrude(height=ret_t+0.2) rr(pad_w-3,pad_h-3,1.5);
    for(dx=[-ret_sx,ret_sx],dy=[-ret_sy,ret_sy]) translate([dx,dy,-0.1]) cylinder(d=screw_hole,h=ret_t+0.2);
    translate([-6,ret_h/2-8,-0.1]) cube([12,12,ret_t+0.2]);   // FFC exit to the rear
  }
}

// ----- Envelopes for fit checks and renders -----
module pcbs() for(s=["left","right"]) half_pose(s) translate([0,0,pcb_bottom_z]) linear_extrude(height=pcb_t) polygon(board_outline);
module keys() for(s=["left","right"]) half_pose(s) for(k=key_positions)
  translate([k[0],k[1],top_z+5]) rotate([0,0,k[2]]) linear_extrude(height=6.8,scale=0.91) rr(17.5,17.5,1);
module knobs() for(s=["left","right"]) half_pose(s) for(e=encoder_positions) translate([e[0],e[1],top_z+2.8]) cylinder(d=13,h=9);
module battery() translate([0,bat_y+bat_l/2,plate_t+0.65+bat_t/2]) cube([bat_w,bat_l,bat_t],center=true);
module carrier() translate([0,car_y,car_z+car_t/2]) cube([car_w,car_l,car_t],center=true);
module padface() pad_pose() translate([0,0,top_z-ov_t+0.03]) linear_extrude(height=ov_t-0.2) rr(ov_w,ov_h,2);

if(part=="shell") shell();
else if(part=="bottom") bottom();
else if(part=="retainer") retainer();
else if(part=="keys") keys();
else if(part=="pcbs") pcbs();
else if(part=="knobs") knobs();
else if(part=="battery") battery();
else if(part=="carrier") carrier();
else if(part=="padface") padface();
else { shell(); translate([0,0,-0.1]) bottom(); pcbs(); keys(); knobs(); battery(); carrier(); padface(); }
