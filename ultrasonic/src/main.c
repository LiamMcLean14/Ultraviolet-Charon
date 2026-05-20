#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/kernel.h>
#include <stdio.h>
#include <stdbool.h>

#define BLENDING_FACTOR 0.8

// Represents state in mm and mm/s
typedef struct {
    float distance;
    float velocity;
} state_vector;

state_vector kalman_filter_step(state_vector prev_state, float measured_distance, float dt,
                                float blending_factor)
{
    // Predict. We predict that velocity is constant, and distance changes by that velocity
    state_vector predicted_state;
    predicted_state.distance = prev_state.distance + prev_state.velocity * dt;
    predicted_state.velocity = prev_state.velocity;

    // Update. We blend the measured distance and velocity with the predicted distance and velocity
    state_vector new_state;
    float measured_velocity = measured_distance - prev_state.distance;
    // Blending factor is assumed to be between 0 and 1
    new_state.distance =
        (1 - blending_factor) * predicted_state.distance + blending_factor * measured_distance;
    new_state.velocity =
        (1 - blending_factor) * predicted_state.velocity + blending_factor * measured_velocity;
    return new_state;
}

float sensor_to_mm(struct sensor_value distance)
{
    return 1000 * distance.val1 + distance.val2 * 0.001;
}

int main(void)
{
    const struct device *dev;
    struct sensor_value distance;
    float measured_distance_mm;
    state_vector current_state;
    bool initialised_state = false;

    dev = DEVICE_DT_GET(DT_ALIAS(ultrasonic0));

    if (!device_is_ready(dev)) {
        printf("HC-SR04 not ready\n");
        return 0;
    }

    while (1) {
        int rc;

        rc = sensor_sample_fetch(dev);
        if (rc < 0) {
            printf("Sample fetch error: %d\n", rc);
            continue;
        }

        rc = sensor_channel_get(dev, SENSOR_CHAN_DISTANCE, &distance);

        if (rc < 0) {
            printf("Channel get error: %d\n", rc);
            continue;
        }

        measured_distance_mm = sensor_to_mm(distance);

        // Either initialise state or update with kalman filter
        if (!initialised_state) {
            current_state.distance = measured_distance_mm;
            current_state.velocity = 0;
            initialised_state = true;
        } else {
            current_state =
                kalman_filter_step(current_state, measured_distance_mm, 0.1, BLENDING_FACTOR);
        }

        printf("Measured: %04f cm, Predicted: %04f cm, Velocity: %04f cm/s\n",
               (measured_distance_mm / 10), (current_state.distance / 10),
               (current_state.velocity / 10));

        k_sleep(K_MSEC(100));
    }

    return 0;
}
