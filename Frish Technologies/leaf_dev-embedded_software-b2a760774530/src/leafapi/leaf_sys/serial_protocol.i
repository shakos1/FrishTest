%module serial_protocol

%include <pybuffer.i>
%include "stdint.i"

%include types.h
%include utils.h
%include serial_protocol/serial_protocol.h

sp_tr_frame_t tr_frame;
sp_rx_ctrl_t rx_ctrl;

int get_tx_size(sp_tr_frame_t *p_frame);
int get_frame_maximum_size(void);

int get_req_size(sp_packet_t *packet);

%pybuffer_binary(char *str, size_t size1);
int frame_to_bytes(char *str, size_t size1, sp_tr_frame_t *p_frame);

%pybuffer_binary(char *data, size_t data_len);
int packet_to_frame(char *data, size_t data_len, sp_packet_t *packet, sp_tr_frame_t *p_frame);

%pybuffer_binary(char *str, size_t size1);
int packet_data_to_bytes(char *str, size_t size1, sp_packet_t *packet);

int get_data_prom_packet(sp_packet_t *packet);
%{
#include "types.h"
#include "serial_protocol.h"

sp_tr_frame_t tr_frame;
sp_rx_ctrl_t rx_ctrl;


int frame_to_bytes(char *str, size_t size, sp_tr_frame_t *p_frame)
{
    int tx_size = GET_TX_SIZE(p_frame);
    if (size < tx_size)
        return -1;
    memcpy(str, p_frame, tx_size);
    return tx_size;
}

int get_frame_maximum_size(void)
{
    return sizeof(sp_tr_frame_t);
}

int get_tx_size(sp_tr_frame_t *p_frame)
{
    return GET_TX_SIZE(p_frame);
}

int packet_to_frame(char *data, size_t data_len, sp_packet_t *packet, sp_tr_frame_t *p_frame)
{
    memcpy(p_frame->payload, packet, sizeof(sp_packet_t));
    if (data_len > 0)
        memcpy(&p_frame->payload[sizeof(sp_packet_t) - 1], data, data_len);
    return 0;
}

int get_req_size(sp_packet_t *packet)
{
    return GET_REQ_PACKET_SIZE(packet);
}

int get_data_prom_packet(sp_packet_t *packet)
{
    return packet->data[0];
}

int packet_data_to_bytes(char *str, size_t size1, sp_packet_t *packet)
{
    if (size1 < packet->data_len)
        return -1;
    memcpy(str, packet->data, packet->data_len);
    return packet->data_len;
}

%}
