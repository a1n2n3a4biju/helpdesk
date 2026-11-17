const API_BASE_URL = "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {

    try {

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {

            ...options,

            headers: {

                "Content-Type": "application/json",

                ...options.headers,

            },

        });

        const data = await response.json();

        if (!response.ok) {

            throw {

                status: response.status,

                detail: data.detail || "Something went wrong",

            };

        }

        return data;

    } catch (error) {

        if (error.status) {

            throw error;

        }

        throw {

            status: 0,

            detail: "Cannot connect to the backend. Please check whether FastAPI is running.",

        };

    }

}
 