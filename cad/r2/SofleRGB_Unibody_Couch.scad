/*
 Sofle RGB + TPS43, elegant integrated couch case (concept revision 2).
 Source positions: Josef Adamcik's official Sofle RGB KiCad PCB, MIT.

 One continuous top shell, separate service bottom, and screw-in trackpad
 retaining frame. The complete assembled keyboard is one rigid enclosure.

 IMPORTANT: Confirm real MX switch/plate stack height, OLED presence,
 trackpad overlay dimensions, and USB-C connector before manufacturing.
 The battery power-distribution circuit is a separate engineering item.
*/

include <sofle_rgb_geometry.scad>;
include <sofle_components.scad>;

part = "assembly";              // "shell", "bottom", "trackpad_frame", "assembly"
$fn = 48;

// ----- Main plan, mm -----
gap = 17;
side_margin = 10;
end_margin = 12;
trackpad_zone = 66;
corner_r = 12;

// ----- Height and installation -----
top_z = 17.5;                 // Overall main shell height (keycaps rise above this)
top_skin_t = 1.8;            // Switch-hole panel; inspect MX clip engagement
perimeter_wall_t = 3.2;
pcb_bottom_z = 9.0;          // Bottom of existing PCB; PCB top is 10.6 mm
pcb_t = 1.6;
panel_bottom_t = 1.8;       // Removable service bottom panel
board_clearance = 0.65;

// ----- Trackpad face and retention -----
pad_cy_shift = 8;            // Move pad back; leaves battery room in front
pad_module_w = 43;
pad_module_h = 40;
pad_overlay_w = 47.5;       // Separate 0.7 mm Mylar/glass overlay
pad_overlay_h = 44;
pad_overlay_t = 0.75;
pad_recess_extra = 0.15;
pad_window_w = 44.0;
pad_window_h = 40.8;
pad_corner_r = 2.0;
pad_retainer_w = 59;
pad_retainer_h = 54;
pad_retainer_t = 2;
pad_frame_screw_x = 26.5;
pad_frame_screw_y = 24;
pad_frame_top_z = 13.25;

// ----- Battery (ONE protected 3.7 V cell) -----
battery_w = 42;             // Prototype envelope; not a battery model number
battery_h = 31;
battery_t = 6;
battery_cy = 25;
battery_edge_gap = 2;
battery_guide_h = 2.2;         // Printed guides; use removable battery-safe tape
battery_guide_t = 1.6;

// ----- Panel connector openings -----
usb_open_w = 11.0;
usb_open_h = 5.1;
usb_center_z = 8.8;
switch_open_w = 10.0;
switch_open_h = 4.2;
switch_center_z = 8.8;
usb_shift_x = -5.0;
usb_mount_pitch = 21.0;        // Adjustable; match the selected USB-C extension
usb_mount_boss_d = 6.8;

// ----- Mounting details -----
boss_outer_d = 7.4;
m2_insert_d = 3.2;         // Confirm insert OD with its datasheet
m2_insert_depth = 3.2;
case_hole_d = 2.3;
pcb_mounts_enabled = true;
oled_windows = false;       // True ONLY if keeping OLED screens
oled_window_w = 27;
oled_window_h = 13;
mx_hole = 14.25;            // Fit-test before a full shell print
encoder_shaft_hole_d = 7.5;

// ----- Derived dimensions -----
case_w = 2*board_w + gap + trackpad_zone + 2*side_margin;
case_h = board_h + 2*end_margin;
left_x = side_margin;
right_x = side_margin + board_w + gap;
board_y = end_margin;
pad_zone_x = right_x + board_w;
pad_cx = pad_zone_x + trackpad_zone/2;
pad_cy = case_h/2 + pad_cy_shift;
shell_under_top = top_z-top_skin_t;
pcb_top_z = pcb_bottom_z+pcb_t;
usb_x = pad_cx+usb_shift_x;
power_x = case_w-16;
bottom_screw_positions = [
  [7.6,7.6], [case_w/3,5.2], [2*case_w/3,5.2], [case_w-7.6,7.6],
  [7.6,case_h-7.6], [case_w/3,case_h-5.2],
  [2*case_w/3,case_h-5.2], [case_w-7.6,case_h-7.6]
];

assert(trackpad_zone>=pad_retainer_w+5,"Trackpad zone too narrow");
assert(battery_w+2*battery_edge_gap<trackpad_zone-5,"Battery too wide");
assert(battery_cy+battery_h/2+4 < pad_cy-pad_overlay_h/2,"Battery and pad overlap in plan");
assert(pcb_top_z+3.6<shell_under_top,"Not enough switch/PCB headroom");

module rr(w,h,r) {
    offset(r=r) offset(delta=-r) square([w,h],center=true);
}

module board_pose(side) {
    if(side=="left")
      translate([left_x+board_w,board_y,0]) mirror([1,0,0]) children();
    else
      translate([right_x,board_y,0]) children();
}

module case_plan_2d(inset=0) {
    translate([case_w/2,case_h/2]) rr(case_w-2*inset,case_h-2*inset,max(1,corner_r-inset));
}

// Outer vertical sides with a 1.2 mm chamfer close to the top surface.
module case_outer() {
    union() {
      linear_extrude(height=top_z-1.2) case_plan_2d();
      hull() {
        translate([0,0,top_z-1.2]) linear_extrude(height=0.01) case_plan_2d();
        translate([0,0,top_z-0.01]) linear_extrude(height=0.01) case_plan_2d(1.2);
      }
    }
}

module switch_cutouts() {
   for(side=["left","right"]) {
      board_pose(side)
        for(k=key_positions)
          translate([k[0],k[1],shell_under_top-0.15])
            rotate([0,0,k[2]])
              linear_extrude(height=top_skin_t+0.5)
                square([mx_hole,mx_hole],center=true);
      board_pose(side)
        for(e=encoder_positions)
          translate([e[0],e[1],shell_under_top-0.15])
            cylinder(d=encoder_shaft_hole_d,h=top_skin_t+0.5);
   }
}

module oled_cutouts() {
   if(oled_windows)
     for(side=["left","right"])
       board_pose(side)
         translate([96.7-82.05,146.8-74.6,shell_under_top-0.2])
           linear_extrude(height=top_skin_t+0.6)
             rr(oled_window_w,oled_window_h,2);
}

// Trackpad supports an overlay via a shallow top recess and a smaller
// opening below it. The 1.75 mm surrounding ledge prevents drop-through.
module pad_face_cutouts() {
   translate([pad_cx,pad_cy,top_z-pad_overlay_t-pad_recess_extra])
     linear_extrude(height=pad_overlay_t+pad_recess_extra+0.25)
       rr(pad_overlay_w,pad_overlay_h,pad_corner_r);
   translate([pad_cx,pad_cy,shell_under_top-0.2])
     linear_extrude(height=top_skin_t+0.45)
       rr(pad_window_w,pad_window_h,pad_corner_r);
}

// Rear panel USB-C cutout plus a separate recessed slide-switch window.
module port_cutouts() {
    translate([usb_x-usb_open_w/2,case_h-7,usb_center_z-usb_open_h/2])
      cube([usb_open_w,8,usb_open_h]);
    translate([power_x-switch_open_w/2,case_h-7,switch_center_z-switch_open_h/2])
      cube([switch_open_w,8,switch_open_h]);
    // Service reset pinhole near the USB-C connector.
    translate([usb_x-19,case_h-7,usb_center_z])
      rotate([-90,0,0]) cylinder(d=2.0,h=8);
}

module pcb_support_bosses() {
    if(pcb_mounts_enabled)
      for(side=["left","right"])
        board_pose(side) for(h=board_mount_holes)
          translate([h[0],h[1],pcb_top_z])
            difference() {
              cylinder(d=boss_outer_d,h=shell_under_top-pcb_top_z+0.5);
              translate([0,0,-0.1])
                cylinder(d=m2_insert_d,h=m2_insert_depth+0.1);
            }
}

module pad_mount_bosses() {
    for(dx=[-pad_frame_screw_x,pad_frame_screw_x],dy=[-pad_frame_screw_y,pad_frame_screw_y])
      translate([pad_cx+dx,pad_cy+dy,pad_frame_top_z])
        difference() {
          cylinder(d=7.5,h=shell_under_top-pad_frame_top_z+0.5);
          translate([0,0,-0.1]) cylinder(d=m2_insert_d,h=m2_insert_depth+0.1);
        }
}

module bottom_mount_bosses() {
    for(p=bottom_screw_positions)
      translate([p[0],p[1],panel_bottom_t])
        difference(){
          cylinder(d=6.2,h=4);
          translate([0,0,-0.1]) cylinder(d=m2_insert_d,h=m2_insert_depth+0.1);
        }
}

// Two internal M2 insert bosses anchor a short female-to-male USB-C panel
// extension. Confirm the real connector flange hole pitch before fabrication.
module usb_connector_bosses() {
    for(dx=[-usb_mount_pitch/2,usb_mount_pitch/2])
      translate([usb_x+dx,case_h-9.3,usb_center_z])
        rotate([-90,0,0])
          difference(){
            cylinder(d=usb_mount_boss_d,h=6.5);
            translate([0,0,-0.1])
              cylinder(d=m2_insert_d,h=m2_insert_depth+0.1);
          }
}

module main_shell() {
  union() {
    difference() {
      case_outer();
      // Hollow underside. Insert both assembled PCB halves from below.
      translate([0,0,-0.05])
        linear_extrude(height=shell_under_top+0.05)
          case_plan_2d(perimeter_wall_t);
      switch_cutouts();
      oled_cutouts();
      pad_face_cutouts();
      port_cutouts();
    }
    pcb_support_bosses();
    pad_mount_bosses();
    bottom_mount_bosses();
    usb_connector_bosses();
  }
}

// Separate 1.8mm bottom service panel. It protects solder joints and cell.
module service_bottom() {
    union() {
      difference() {
        linear_extrude(height=panel_bottom_t)
          case_plan_2d(perimeter_wall_t+0.55);
        for(p=bottom_screw_positions)
          translate([p[0],p[1],-0.1]) cylinder(d=case_hole_d,h=panel_bottom_t+0.2);
      }
      // Four low-profile removable-cell guides. Battery-safe tape retains
      // the protected pouch cell. Avoid screws or sharp points over the cell.
      for(dx=[-1,1],dy=[-1,1])
        translate([pad_cx+dx*(battery_w/2+1.3),
                   battery_cy+dy*(battery_h/2+1.2),panel_bottom_t])
          linear_extrude(height=battery_guide_h)
            rr(5.0,5.0,1.0);
    }
}

module trackpad_retainer() {
  difference() {
    linear_extrude(height=pad_retainer_t)
      rr(pad_retainer_w,pad_retainer_h,4);
    // Center relief: contact is applied only around module perimeter.
    translate([0,0,-0.1])
      linear_extrude(height=pad_retainer_t+0.2)
        rr(pad_module_w-3,pad_module_h-3,1.5);
    for(dx=[-pad_frame_screw_x,pad_frame_screw_x],dy=[-pad_frame_screw_y,pad_frame_screw_y])
      translate([dx,dy,-0.1]) cylinder(d=case_hole_d,h=pad_retainer_t+0.2);
    // FFC cable exits the retaining frame toward the rear of the case.
    translate([-6,pad_retainer_h/2-8,-0.1])
      cube([12,12,pad_retainer_t+0.2]);
  }
}

module pcb_ghost(side){
  board_pose(side)
    translate([0,0,pcb_bottom_z])
      linear_extrude(height=pcb_t) polygon(board_outline);
}

module keycaps_ghost(side){
  board_pose(side)
    for(k=key_positions)
      translate([k[0],k[1],top_z+5.0])
        rotate([0,0,k[2]])
          linear_extrude(height=6.8,scale=0.91)
            rr(17.5,17.5,1.0);
}

module encoder_knobs_ghost(side){
  board_pose(side)
    for(e=encoder_positions)
      translate([e[0],e[1],top_z+2.8])
        cylinder(d=13,h=9.0);
}

module assembly() {
  color([0.18,0.20,0.23]) main_shell();
  color([0.28,0.30,0.34]) translate([0,0,-0.1]) service_bottom();
  for(side=["left","right"]) {
     color([0.07,0.32,0.25]) pcb_ghost(side);
     color([0.91,0.90,0.85]) keycaps_ghost(side);
     color([0.32,0.34,0.37]) encoder_knobs_ghost(side);
  }
  color([0.07,0.09,0.12])
    translate([pad_cx,pad_cy,top_z-pad_overlay_t+0.03])
      linear_extrude(height=pad_overlay_t-0.2)
        rr(pad_overlay_w,pad_overlay_h,pad_corner_r);
  color([0.22,0.25,0.28])
    translate([pad_cx,pad_cy,pad_frame_top_z-pad_retainer_t]) trackpad_retainer();
  color([0.24,0.46,0.65])
    translate([pad_cx,battery_cy,panel_bottom_t+0.65+battery_t/2])
      cube([battery_w,battery_h,battery_t],center=true);
}

if(part=="shell") main_shell();
else if(part=="bottom") service_bottom();
else if(part=="trackpad_frame") trackpad_retainer();
else assembly();
