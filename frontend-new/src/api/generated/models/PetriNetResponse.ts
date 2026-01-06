/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PetriNetArc } from './PetriNetArc';
import type { PetriNetPlace } from './PetriNetPlace';
import type { PetriNetTransition } from './PetriNetTransition';
/**
 * Petri net structure for visualization.
 */
export type PetriNetResponse = {
    places: Array<PetriNetPlace>;
    transitions: Array<PetriNetTransition>;
    arcs: Array<PetriNetArc>;
    initial_marking: Array<string>;
    final_marking: Array<string>;
};

