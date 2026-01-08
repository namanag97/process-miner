/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Algorithm-specific parameters for process discovery.
 *
 * Different mining algorithms support different parameters:
 * - inductive/inductive_infrequent: noise_threshold (0.0-1.0)
 * - heuristics: dependency_threshold (0.0-1.0), and_threshold (0.0-1.0)
 * - ilp: alpha (0.0-1.0)
 * - log_skeleton: noise_threshold (0.0-1.0)
 */
export type AlgorithmParameters = {
    /**
     * Filter infrequent behavior (0.0-1.0). Used by inductive, log_skeleton miners.
     */
    noise_threshold?: (number | null);
    /**
     * Minimum dependency measure (0.0-1.0). Used by heuristics miner. Default: 0.5
     */
    dependency_threshold?: (number | null);
    /**
     * Minimum AND threshold (0.0-1.0). Used by heuristics miner. Default: 0.65
     */
    and_threshold?: (number | null);
    /**
     * Noise filtering (0.0-1.0). Used by ILP miner. Default: 1.0 (no filtering)
     */
    alpha?: (number | null);
    /**
     * Direction for transition system. Default: forward
     */
    direction?: (string | null);
    /**
     * Window size for transition system. Default: 2
     */
    window?: (number | null);
};

