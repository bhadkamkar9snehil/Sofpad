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
rear_bump = 8;         // extra depth of the centre rear bay (carrier, USB-C, switch)
bay_hw = 36;           // half width of the rear bay before the margin
wall = 3.2;

// ----- Heights -----
pcb_bottom_z = 9.0;
pcb_t = 1.6;
pcb_top_z = pcb_bottom_z + pcb_t;
mx_below_plate = 5.0;  // Cherry MX: PCB top to plate underside
skin_t = 1.5;          // MX clips need a 1.2-1.6 mm plate
under_top = pcb_top_z + mx_below_plate;
top_z = under_top + skin_t;   // 17.1
plate_t = 1.8;
edge_r = 2.0;          // top edge radius, built from 5 steps

// ----- Centre trackpad: Azoteq TPS65-201A-S (adhesive-only module, Azoteq datasheet v1.02) -----
// The module is glued to the underside of a 1.0 mm printed skin. No window, no overlay part.
pad_w = 65;  pad_h = 49;  pad_t = 2.03;      // module outline and thickness incl. adhesive
pad_skin = 1.0;                              // skin thickness over the pad (limit 1.2)
pad_top_z = top_z - pad_skin;                // module top face
pad_cx = 0;  pad_cy = 26;
ret_ring_w = 69; ret_ring_h = 53;            // retainer ring outer
ret_in_w = 61;   ret_in_h = 45;              // ring opening: 2 mm contact on the module edge
boss_bottom = under_top - 4.0;               // pad bosses hang 4 mm from the skin
ret_t = 2;                                   // ear thickness, under the boss
ret_screws = [[-20,-29],[20,-29],[-20,29],[20,29]];   // relative to pad centre
// ----- Behind the pad: battery (lying) then carrier -----
bat_w = 52; bat_l = 36; bat_t = 8;  bat_y0 = 59;     // NOVA 603450: 50 x 34 x 6 plus margin
car_w = 62; car_l = 28; car_t = 1.0; car_z = 3.0;    // carrier envelope, underside height
usb_x = -10; sw_x = 12;
usb_w = 11; usb_h = 5.1; sw_w = 10; sw_h = 4.2; port_z = 5.7;   // centres: board top 4.0 + half the part height

mx_hole = 14.25;
enc_hole = 7.5;
insert_d = 3.2; insert_depth = 3.2; screw_hole = 2.3;

// ----- Single large screen: 2.0 in 240x320 IPS (ST7789), portrait, between the halves -----
scr_w = 36; scr_h = 54; scr_t = 4.0;          // module envelope
scr_win_w = 31.6; scr_win_h = 41.8;           // active area 30.6 x 40.8 plus 0.5 per side
scr_cy = 88; scr_win_dy = 2;                   // module centre y; window offset toward top

hy = board_h*cos(ang);
hx = g/2 - board_h*sin(ang);
y_rear = hy + rear_bump + margin;
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
  translate([-bay_hw,hy-10]) square([2*bay_hw,10+rear_bump]);   // rear bay
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
}
module screen_cut() translate([0,scr_cy+scr_win_dy,under_top-0.2]) linear_extrude(height=skin_t+0.5) rr(scr_win_w,scr_win_h,1.5);
// Pocket frame under the skin holds the module in plan; foam tape holds it up.
module screen_frame() translate([0,scr_cy,under_top-scr_t-0.2]) difference() {
  linear_extrude(height=scr_t+0.4) rr(scr_w+3.6,scr_h+3.6,2);
  translate([0,0,-0.1]) linear_extrude(height=scr_t+0.6) rr(scr_w+0.4,scr_h+0.4,1.5);
}
module pad_cuts() translate([pad_cx,pad_cy,under_top-0.2]) linear_extrude(height=pad_top_z-under_top+0.2)
  rr(pad_w+0.4,pad_h+0.4,2);    // pocket in the skin underside: leaves a 1.0 mm skin
module port_cuts() {
  translate([usb_x-usb_w/2,y_rear-7,port_z-usb_h/2]) cube([usb_w,8,usb_h]);
  translate([sw_x-sw_w/2,y_rear-7,port_z-sw_h/2]) cube([sw_w,8,sw_h]);
}

// ----- Bosses -----
module insert_boss(d,h) difference() { cylinder(d=d,h=h); translate([0,0,-0.1]) cylinder(d=insert_d,h=insert_depth+0.1); }
module insert_boss_top(d,h) difference() { cylinder(d=d,h=h); translate([0,0,h-insert_depth]) cylinder(d=insert_d,h=insert_depth+0.1); }
module pcb_bosses() for(s=["left","right"]) half_pose(s) for(h=board_mount_holes)
  translate([h[0],h[1],pcb_top_z]) insert_boss(7.4,under_top-pcb_top_z+0.5);
module pad_bosses() translate([pad_cx,pad_cy,0]) for(q=ret_screws)
  translate([q[0],q[1],boss_bottom]) insert_boss(7,under_top-boss_bottom+0.5);

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
      key_cuts(); pad_cuts(); screen_cut(); port_cuts();
    }
    pcb_bosses(); pad_bosses(); plate_bosses(); screen_frame();
  }
}
module bottom() {
  difference() {
    linear_extrude(height=plate_t) plan(wall+0.55);
    for(p=screws) translate([p[0],p[1],-0.1]) cylinder(d=screw_hole,h=plate_t+0.2);
  }
  for(dx=[-1,1],dy=[-1,1]) translate([dx*(bat_w/2+1.3),bat_y+dy*(bat_l/2+1.2),plate_t-0.2]) linear_extrude(height=2.4) rr(5,5,1);
  // carrier: four foam pads under the corners and four locator posts at the edges (no screws)
  for(sx=[-1,1],sy=[-1,1]) {
    translate([sx*(car_w/2-4),car_y+sy*(car_l/2-4),plate_t-0.2]) linear_extrude(height=car_z-plate_t+0.2) square([8,8],center=true);
    translate([sx*(car_w/2+0.9),car_y+sy*(car_l/2-4),plate_t-0.2]) linear_extrude(height=car_z+car_t-plate_t+0.2) square([1.6,8],center=true);
  }
}
// Retainer: ring that carries the module edge, four ears that screw up into the pad bosses.
module retainer() {
  ring_h = pad_top_z - pad_t - (boss_bottom - ret_t);          // ring top meets the module underside
  difference() {
    union() {
      linear_extrude(height=ring_h) rr(ret_ring_w,ret_ring_h,3);
      for(q=ret_screws) hull() {
        translate([q[0],q[1]*0.5]) linear_extrude(height=ret_t) square([8,4],center=true);
        translate([q[0],q[1]]) linear_extrude(height=ret_t) circle(d=7);
      }
    }
    translate([0,0,-0.1]) linear_extrude(height=ring_h+0.2) rr(ret_in_w,ret_in_h,2);
    for(q=ret_screws) translate([q[0],q[1],-0.1]) cylinder(d=screw_hole,h=ret_t+0.2);
    translate([-6,ret_ring_h/2-6,-0.1]) cube([12,8,ring_h+0.2]);    // FFC exit to the rear
  }
}

// ----- Envelopes (fit checks and renders) -----
module pcbs() for(s=["left","right"]) half_pose(s) translate([0,0,pcb_bottom_z]) linear_extrude(height=pcb_t) polygon(board_outline);
module switches() for(s=["left","right"]) half_pose(s) for(k=key_positions)
  translate([k[0],k[1],top_z]) rotate([0,0,k[2]]) linear_extrude(height=3.3) square([15.6,15.6],center=true);
module keys() for(s=["left","right"]) half_pose(s) for(k=key_positions)
  translate([k[0],k[1],top_z+3.5]) rotate([0,0,k[2]]) linear_extrude(height=7.4,scale=0.70) rr(18.2,18.2,1.5);
module knobs() for(s=["left","right"]) half_pose(s) for(e=encoder_positions) translate([e[0],e[1],top_z+2.8]) cylinder(d=13,h=9);
module battery() translate([0,bat_y,plate_t+0.65+bat_t/2]) cube([bat_w,bat_l,bat_t],center=true);
module carrier() translate([0,car_y,car_z+car_t/2]) cube([car_w,car_l,car_t],center=true);
module padface() translate([pad_cx,pad_cy,top_z-0.05]) linear_extrude(height=0.08) rr(pad_w,pad_h,2);
module padbody() translate([pad_cx,pad_cy,pad_top_z-pad_t]) linear_extrude(height=under_top-(pad_top_z-pad_t)) rr(pad_w,pad_h,2);   // part below the skin
module retainer_placed() translate([pad_cx,pad_cy,boss_bottom-ret_t]) retainer();
module screen_body() translate([0,scr_cy,under_top-scr_t/2]) cube([scr_w,scr_h,scr_t],center=true);
// Pro Micro adapters: soldered straight into the Sofle U1 holes (plastic spacer removed), 18 x 39.5 mm,
// FFC connector on the end that points at the PCB edge. Local half-frame position from the Sofle KiCad file.
adp_x = 17.75; adp_y = 94.7; adp_w = 18; adp_l = 40; adp_t = 1.0; adp_conn = 2.0; adp_gap = 0.5;
module adapter_boards() for(s=["left","right"]) half_pose(s) translate([adp_x-adp_w/2,adp_y-adp_l/2,pcb_top_z+adp_gap]) cube([adp_w,adp_l,adp_t]);
module adapter_conns() for(s=["left","right"]) half_pose(s) translate([adp_x-7.1,adp_y+adp_l/2-8.3,pcb_top_z+adp_gap+adp_t]) cube([14.2,8,adp_conn]);
module adapters() for(s=["left","right"]) half_pose(s)
  translate([adp_x,adp_y,pcb_top_z+adp_gap]) {
    color([0.05,0.30,0.22]) translate([-adp_w/2,-adp_l/2,0]) cube([adp_w,adp_l,adp_t]);
    color([0.9,0.88,0.8]) translate([-7.1,adp_l/2-8.3,adp_t]) cube([14.2,8,adp_conn]);
  }
module adapter_body() union() { for(s=["left","right"]) half_pose(s)
  translate([adp_x-adp_w/2,adp_y-adp_l/2,pcb_top_z+adp_gap]) cube([adp_w,adp_l,adp_t+adp_conn]); }
module cavity() translate([0,0,plate_t]) linear_extrude(height=under_top-plate_t) plan(wall);
module usb_env() translate([usb_x,y_rear-wall-3.6,port_z]) cube([9,6,3.3],center=true);

module by_name(n) {
  if(n=="battery") battery(); else if(n=="carrier") carrier(); else if(n=="pcbs") pcbs();
  else if(n=="padbody") padbody(); else if(n=="retainer") retainer_placed(); else if(n=="cavity") cavity();
  else if(n=="bosses") { pcb_bosses(); pad_bosses(); } else if(n=="platebosses") plate_bosses();
  else if(n=="adapters") adapter_body();
  else if(n=="usb") usb_env(); else if(n=="screen") screen_body();
}

if(part=="shell") shell();
else if(part=="bottom") bottom();
else if(part=="retainer") retainer();
else if(part=="retainer_placed") retainer_placed();
else if(part=="keys") keys();
else if(part=="switches") switches();
else if(part=="adapters") adapter_boards();
else if(part=="adapter_conns") adapter_conns();
else if(part=="screen") screen_body();
else if(part=="padbody") padbody();
else if(part=="pcbs") pcbs();
else if(part=="knobs") knobs();
else if(part=="battery") battery();
else if(part=="carrier") carrier();
else if(part=="padface") padface();
else if(part=="overlap") intersection(){ by_name(chk_a); by_name(chk_b); }
else if(part=="outside") difference(){ by_name(chk_a); by_name(chk_b); }
else { shell(); translate([0,0,-0.1]) bottom(); pcbs(); switches(); keys(); knobs(); battery(); carrier(); padface(); retainer_placed(); }
