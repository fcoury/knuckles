"""Pinned JLC stackup and the vendor-calculated USB routing geometry."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
PROFILE={
    'name':'JLC04161H-3313','nominal_board_mm':1.6,'vendor_finished_mm':1.56,
    'finished_tolerance_percent':10,'outer_copper_mm':.035,'inner_copper_mm':.0152,
    'prepreg_mm':.0994,'prepreg_er':4.1,'core_mm':1.265,'core_er':4.6,
    'usb':{'target_ohms':90,'width_mm':.1356,'gap_mm':.1501,'signal_layer':'F.Cu',
           'reference_layer':'In1.Cu','model':'Differential Pair (Non coplanar), with solder mask',
           'same_layer_copper_review_target_mm':.5,
           'review_limit':'Inspect nearby routed pads/vias/traces; geometry alone does not certify impedance'},
    'sources':['https://jlcpcb.com/impedance','https://jlcpcb.com/pcb-impedance-calculator'],
    'checked_at':'2026-10-18','calculator_inputs':'4 layers, 1.6mm, outer 1oz, inner 0.5oz, 90ohm, 0.15mm pair spacing',
    'kicad_mask_note':'0.01524mm models the mask over copper; substrate coating is thicker. Vendor calculator remains the impedance source.',
    'source_limit':'Calculator geometry is a design target; vendor stack and impedance control must be selected in the actual order.'
}
def apply(board_path):
    # KiCad 8 exposes the descriptor as an opaque SWIG object. Write its native
    # s-expression, which is subsequently parsed by KiCad during verification.
    text=board_path.read_text()
    assert '(stackup' not in text,'Apply only once to a fresh generated board'
    block='''(stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01524) (epsilon_r 3.8))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "3313") (epsilon_r 4.1) (loss_tangent 0.02))
      (layer "In1.Cu" (type "copper") (thickness 0.0152))
      (layer "dielectric 2" (type "core") (thickness 1.265) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
      (layer "In2.Cu" (type "copper") (thickness 0.0152))
      (layer "dielectric 3" (type "prepreg") (thickness 0.0994) (material "3313") (epsilon_r 4.1) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01524) (epsilon_r 3.8))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "ENIG")
      (dielectric_constraints yes)
    )'''
    board_path.write_text(text.replace('(setup','(setup\n    '+block,1))
    (HERE/'references/stackup.json').write_text(json.dumps(PROFILE,indent=2)+'\n')
