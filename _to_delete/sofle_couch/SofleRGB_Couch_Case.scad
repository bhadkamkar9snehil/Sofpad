/*
  Sofle RGB couch keyboard: one-piece 3D-printable lower enclosure.
  Both existing PCB halves remain separate electrical boards inside one shell.
  A right-side Azoteq TPS43 touchpad sits in an integrated, recessed deck.

  Import the source-specific geometry from sofle_rgb_geometry.scad.
  Dimensions are in mm. Edit the parameters, then render part="case".

  CAUTION: This fits Josef Adamcik's official Sofle RGB PCB geometry.
  Check dimensions and mounting holes before printing if you have a clone.
*/

include <sofle_rgb_geometry.scad>;

// ------- Main user parameters -------
part = "assembly";                   // "assembly" | "case" | "pad_coupon"
pcb_revision_clearance = 0.8;        // Radial relief around PCB perimeter
half_gap = 17;                       // Space between the two PCB envelopes
edge_margin = 10;                    // Minimum outside border, X
end_margin = 12;                     // Minimum outside border, Y
pad_zone_w = 66;                     // Width reserved for touchpad and its electronics
outer_corner_r = 11;

// ------- Vertical structure -------
floor_t = 3.0;                       // Base plate thickness
pcb_bottom_z = 12.0;                 // PCB bottom face height from case underside
pcb_t = 1.6;                         // Source PCB thickness; confirm with calipers
wall_top_z = 11.5;                   // Keep wall below PCB and keycap skirts
pad_deck_z = 15.0;                   // Touchpad deck top height

// ------- Mounting hardware -------
boss_d = 7.0;
boss_fillet_r = 0.5;
insert_hole_d = 3.2;                 // TEST: M2 insert vendor hole specification
insert_depth = 4.0;                  // TEST: M2 insert height
hole_x_adjust = 0;                  // Only change after measuring PCB itself
hole_y_adjust = 0;

// ------- Trackpad: Azoteq TPS43 -------
pad_w = 43.0;
pad_h = 40.0;
pad_side_clearance = 0.6;           // Clearance on each side
pad_recess_depth = 1.8;             // Tune for actual module + adhesive + overlay
pad_backing_roof_t = 3.6;            // Total skin thickness above underside grid
pad_position_y = 0;                 // Offset from height center
ffc_slot_w = 12;                    // Cable opening, near far/top edge
ffc_slot_h = 6;
pad_pocket_corner_r = 1.2;
pad_grid_cols = 4;                  // Weight-saving cells; bridge widths < 13mm
pad_grid_rows = 7;
pad_grid_rib = 3.0;

// ------- Cable channels -------
link_channel_w = 8;                 // Internal TRRS cable bridge clearance
link_channel_offset_y = 0;          // Align groove with source TRRS connector
link_channel_depth = 5.5;
pad_wire_channel_w = 9;

// ------- Preview and quality -------
$fn = 48;
preview_board = true;
preview_touchpad = true;

// Derived positions. Left = source board mirrored; right = source board as drawn.
case_w = 2 * board_w + half_gap + pad_zone_w + 2 * edge_margin;
case_h = board_h + 2 * end_margin;
left_x = edge_margin;
right_x = edge_margin + board_w + half_gap;
board_y = end_margin;
pad_zone_x = right_x + board_w;
pad_cx = pad_zone_x + pad_zone_w / 2;
pad_cy = case_h / 2 + pad_position_y;
link_channel_y = board_y + board_trrs[1] + link_channel_offset_y;

assert(half_gap >= 12, "Use at least 12 mm between PCB envelopes for the bridge.");
assert(pad_zone_w >= pad_w + 2*pad_side_clearance + 14, "Trackpad bay needs border clearance.");
assert(wall_top_z < pcb_bottom_z, "Wall must stay below the PCB underside.");
assert(pad_recess_depth < pad_deck_z - pad_backing_roof_t - floor_t,
       "Pad recess is too deep.");
assert(pad_backing_roof_t-pad_recess_depth >= 1.5,
       "Keep at least 1.5 mm under the pad pocket.");

module rr2d(w, h, r) {
    offset(r=r) offset(delta=-r) square([w,h], center=true);
}

module case_perimeter_2d() {
    translate([case_w/2, case_h/2]) rr2d(case_w,case_h,outer_corner_r);
}

module board_pose(side) {
    if (side == "left")
        translate([left_x + board_w, board_y, 0]) mirror([1,0,0]) children();
    else
        translate([right_x, board_y, 0]) children();
}

module pcb_perimeter_2d() {
    polygon(points=board_outline);
}

// Forming only the two key PCB cavities leaves a rigid, continuous shell.
module board_cavity(side) {
    board_pose(side)
        translate([0,0,floor_t])
            linear_extrude(height=max(wall_top_z,pcb_bottom_z)+2)
                offset(delta=pcb_revision_clearance) pcb_perimeter_2d();
}

module raw_shell() {
    union() {
        linear_extrude(height=wall_top_z) case_perimeter_2d();
        translate([pad_zone_x + pad_zone_w/2,case_h/2,0])
            linear_extrude(height=pad_deck_z)
                rr2d(pad_zone_w,case_h-0.5,8);
    }
}

// Creates a full-depth recess for a TPS43, with an internal FFC exit.
module trackpad_cutouts() {
    // Pocket cut from the TOP. Leave a solid pad backing surface.
    translate([pad_cx,pad_cy,pad_deck_z-pad_recess_depth])
        linear_extrude(height=pad_recess_depth+1)
            rr2d(pad_w+2*pad_side_clearance,
                 pad_h+2*pad_side_clearance,pad_pocket_corner_r);

    // Open-bottom cellular relief. 10-12 mm cells bridge more easily in FDM.
    // Mount the regulator/shifter in the open right PCB cavity, not here.
    grid_w = pad_zone_w-16;
    grid_h = case_h-30;
    cell_w = (grid_w-(pad_grid_cols-1)*pad_grid_rib)/pad_grid_cols;
    cell_h = (grid_h-(pad_grid_rows-1)*pad_grid_rib)/pad_grid_rows;
    for (col=[0:pad_grid_cols-1], row=[0:pad_grid_rows-1])
        translate([
            pad_cx-grid_w/2+col*(cell_w+pad_grid_rib),
            case_h/2-grid_h/2+row*(cell_h+pad_grid_rib),
            -0.1
        ])
            cube([cell_w,cell_h,pad_deck_z-pad_backing_roof_t+0.1]);

    // Recess for a connector under the sensor near its top edge.
    translate([pad_cx-ffc_slot_w/2,
               pad_cy+pad_h/2-ffc_slot_h,
               pad_deck_z-pad_recess_depth-2.0])
        cube([ffc_slot_w,ffc_slot_h,2.1]);

    // Top-open cable groove from pad recess to the right-hand PCB cavity.
    // Cover the exposed groove after wiring; confirm FFC bend clearance.
    translate([pad_zone_x-2,
               pad_cy+pad_h/2-ffc_slot_h,
               pad_deck_z-pad_recess_depth-2.0])
        cube([pad_zone_w/2+4,ffc_slot_h,pad_recess_depth+2.1]);
}

module split_bridge_channel() {
    // Extend into both PCB cavities. This groove must not be a sealed void.
    translate([left_x+board_w-14,link_channel_y-link_channel_w/2,floor_t])
        cube([half_gap+28,link_channel_w,link_channel_depth]);
}

module boss_at(p) {
    translate([p[0]+hole_x_adjust,p[1]+hole_y_adjust,0]) {
        // An M2 heat-set insert goes into the top of this printed boss.
        difference() {
            translate([0,0,floor_t]) cylinder(h=pcb_bottom_z-floor_t,d=boss_d);
            translate([0,0,pcb_bottom_z-insert_depth])
                cylinder(h=insert_depth+0.5,d=insert_hole_d);
        }
    }
}

module pcb_bosses(side) {
    board_pose(side)
        for (h=board_mount_holes) boss_at(h);
}

module finished_case() {
    union() {
        difference() {
            raw_shell();
            board_cavity("left");
            board_cavity("right");
            split_bridge_channel();
            trackpad_cutouts();
        }
        pcb_bosses("left");
        pcb_bosses("right");
    }
}

module board_ghost(side) {
    board_pose(side)
        translate([0,0,pcb_bottom_z])
            linear_extrude(height=pcb_t) pcb_perimeter_2d();
}

module preview_assembly() {
    color([0.22,0.25,0.28]) finished_case();
    if (preview_board) {
        color([0.08,0.42,0.34,0.7]) board_ghost("left");
        color([0.08,0.42,0.34,0.7]) board_ghost("right");
    }
    if (preview_touchpad)
        color([0.12,0.14,0.16,0.9])
            translate([pad_cx,pad_cy,pad_deck_z-pad_recess_depth+0.25])
                linear_extrude(height=max(0.5,pad_recess_depth-0.5))
                    rr2d(pad_w,pad_h,1.0);
}

// A fast test piece. Print this before a full-length case to verify the pad fit.
module fit_coupon() {
    intersection() {
        finished_case();
        translate([pad_cx-(pad_w/2+9),pad_cy-(pad_h/2+9),-0.1])
            cube([pad_w+18,pad_h+18,pad_deck_z+0.2]);
    }
}

if (part == "case") finished_case();
else if (part == "pad_coupon") fit_coupon();
else preview_assembly();
