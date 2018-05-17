import argparse
from . import pick_and_place
from . import simplify_contact


def main():
    parser = argparse.ArgumentParser(description="Entry point to a collection of programs for object"
                                                 "transportation I wrote while working on a paper.")
    subparsers = parser.add_subparsers()
    # A subparser for the program that computes the robust
    # controllable sets
    parser_pick = subparsers.add_parser('pick-demo', description='')
    parser_pick.set_defaults(which='pick-demo')
    parser_pick.add_argument('-s', "--scene", help="Path to scenario. "
                                                   "Example: scenarios/test0.scenario.yaml",
                             default="scenarios/test0.scenario.yaml")
    parser_pick.add_argument('-v', dest='verbose', action='store_true')
    parser_pick.add_argument('-d', "--slowdown", type=float, default=0.5)
    parser_pick.add_argument('-e', "--execute_hw", help="If True, send commands to real hardware.",
                             action="store_true", default=False)
    parser_sim = subparsers.add_parser('simplify-contact', description="A program for simplifying and converting contact configurations. "
                                                "Contact should contain raw_data field.")
    parser_sim.add_argument('-c', '--contact', help='Contact to be simplified', required=True)
    parser_sim.add_argument('-o', '--object', help='Object specification, use for dynamic exploration (strategy10).', required=False)
    parser_sim.add_argument('-a', '--attach', help='Name of the link or mnaipulator that the object is attached to.', required=False, default="denso_suction_cup")
    parser_sim.add_argument('-T', '--transform', help='T_link_object', required=False, default="[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 9.080e-3], [0, 0, 0, 1]]")
    parser_sim.add_argument('-r', '--robot', help='Robot specification, use for dynamic exploration (strategy10).', required=False, default="suctioncup1")
    parser_sim.add_argument('-v', '--verbose', help='More verbose output', action="store_true")

    args = parser.parse_args()
    if args.which == "pick-demo":
        pick_and_place.main(load_path=args.scene, verbose=args.verbose,
                            execute_hw=args.execute_hw, slowdown=args.slowdown)
    if args.which == "simplify-contact":
        simplify_contact.main(
            contact_id=args.contact,
            object_id=args.object,
            attach=args.attach,
            T_link_object=args.transform,
            robot_id=args.robot,
            verbose=args.verbose
        )

    return 1
