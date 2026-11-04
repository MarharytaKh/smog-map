export interface paths {
    "/stations": {
        get: operations["list_stations_stations_get"];
    };
    "/stations/near": {
        get: operations["near_stations_near_get"];
    };
    "/stations/{station_id}": {
        get: operations["get_station_stations__station_id__get"];
    };
    "/stations/{station_id}/history": {
        get: operations["station_history_stations__station_id__history_get"];
    };
    "/cities": {
        get: operations["list_cities_cities_get"];
    };
    "/cities/ranking": {
        get: operations["ranking_cities_ranking_get"];
    };
    "/cities/{name}": {
        get: operations["city_cities__name__get"];
    };
    "/compare": {
        get: operations["compare_compare_get"];
    };
    "/subscriptions": {
        post: operations["subscribe_subscriptions_post"];
    };
    "/subscriptions/{token}": {
        delete: operations["unsubscribe_subscriptions__token__delete"];
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        CityDetail: {
            city: string;
            stations: components["schemas"]["StationOut"][];
            history: {
                [key: string]: components["schemas"]["Point"][];
            };
        };
        CityRank: {
            city: string;
            value: number;
            index: number | null;
            index_label: string | null;
            stations: number;
        };
        Compare: {
            param: string;
            a: components["schemas"]["CityDetail"];
            b: components["schemas"]["CityDetail"];
        };
        NearStation: {
            id: number;
            name: string;
            city: string;
            lat: number;
            lon: number;
            values: {
                [key: string]: number | null;
            };
            index: number | null;
            index_label: string | null;
            updated_at: string | null;
            distance_km: number;
        };
        Point: {
            ts: string;
            value: number;
        };
        StationOut: {
            id: number;
            name: string;
            city: string;
            lat: number;
            lon: number;
            values: {
                [key: string]: number | null;
            };
            index: number | null;
            index_label: string | null;
            updated_at: string | null;
        };
        SubscriptionIn: {
            email: string;
            lat: number;
            lon: number;
            radius_km?: number;
            threshold?: number;
        };
        SubscriptionOut: {
            token: string;
            email: string;
            lat: number;
            lon: number;
            radius_km: number;
            threshold: number;
            nearest_stations?: components["schemas"]["NearStation"][];
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export type operations = Record<string, unknown>;
