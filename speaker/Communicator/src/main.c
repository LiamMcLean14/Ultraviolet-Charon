:wq
/*
 * Copyright (c) 2024 Croxel, Inc.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/services/nus.h>
#include <zephyr/device.h>
#include <zephyr/drivers/pwm.h>
#include <zephyr/sys/ring_buffer.h>
#include <zephyr/sys/time_units.h>

//PWM SETUP
#define PWM_NODE DT_NODELABEL(speaker_pwm)
static const struct pwm_dt_spec pwm = PWM_DT_SPEC_GET(PWM_NODE);

//1MHz PWM carrier
static const uint32_t pwm_period_ns = PWM_HZ(125000);

#define DEVICE_NAME		CONFIG_BT_DEVICE_NAME
#define DEVICE_NAME_LEN		(sizeof(DEVICE_NAME) - 1)

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

static const struct bt_data sd[] = {
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_NUS_SRV_VAL),
};

static void notif_enabled(bool enabled, void *ctx)
{
	ARG_UNUSED(ctx);

	printk("%s() - %s\n", __func__, (enabled ? "Enabled" : "Disabled"));
}

//Audio Buffer
#define AUDIO_BUFFER_SIZE 16384
RING_BUF_DECLARE(audio_rb, AUDIO_BUFFER_SIZE);

static void received(struct bt_conn *conn, const void *data, uint16_t len, void *ctx)
{
	ARG_UNUSED(conn);
	ARG_UNUSED(ctx);

  const uint8_t *audio = data;

  uint32_t written = ring_buf_put(&audio_rb, audio, len);
  if (written < len) {
    //printk("Ring buffer overflowed\n");
  }
  //printk("%s() - Len: %d, Message: %.*s\n", __func__, len, len, (char *)data);
}

struct bt_nus_cb nus_listener = {
	.notif_enabled = notif_enabled,
	.received = received,
};

void audio_thread(void)
{
    uint8_t sample;
    const uint32_t wait_cycles = k_us_to_cyc_near32(80);
    
    //I cannot for the life of me figure out why this thing plays music slowly. I think the CPU is overloaded.
    while (1) {
        
        uint32_t start_time = k_cycle_get_32();
        if (ring_buf_get(&audio_rb, &sample, 1) == 1) {
            
            uint32_t pulse = (sample * pwm_period_ns) / 255;
            pwm_set_dt(&pwm, pwm_period_ns, pulse);
            
            uint32_t elapsed_cycles = k_cycle_get_32() - start_time;
            
            if (elapsed_cycles < wait_cycles) {
              uint32_t waitPeriod = k_cyc_to_us_near32(wait_cycles - elapsed_cycles);
              //printk("Waiting %d nanoseconds\n", waitPeriod);
              k_busy_wait(waitPeriod);
            } 
        }
        /*else {
            k_sleep(K_USEC(20));
        }*/
    }
}

K_THREAD_DEFINE(audio_tid, 1024, audio_thread, NULL, NULL, NULL, 2, 0, 0);

int main(void)
{
	int err;

	printk("Sample - Bluetooth Peripheral NUS\n");

	err = bt_nus_cb_register(&nus_listener, NULL);
	if (err) {
		printk("Failed to register NUS callback: %d\n", err);
		return err;
	}

	err = bt_enable(NULL);
	if (err) {
		printk("Failed to enable bluetooth: %d\n", err);
		return err;
	}

	err = bt_le_adv_start(BT_LE_ADV_CONN_FAST_1, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
	if (err) {
		printk("Failed to start advertising: %d\n", err);
		return err;
	}

	printk("Initialization complete\n");
  
  //Before starting transmission, buffer a little bit ahead of time to avoid initial stuttering.
  while (ring_buf_size_get(&audio_rb) < 12000) {
      k_sleep(K_MSEC(10));
  }

  printk("Starting playback\n");
  //IDLE
  while (1) {
      k_sleep(K_SECONDS(1));  
  }
	
  return 0;
}

