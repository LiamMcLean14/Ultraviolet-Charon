#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/kernel.h>
#include <stdio.h>

int main(void)
{
    const struct device *dev;
    struct sensor_value distance;

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

        printf("Distance: %d.%06d m\n", distance.val1, distance.val2);

        k_sleep(K_MSEC(500));
    }

    return 0;
}
