"""
Generador del Dataset Multi-Período de Facturas Sanitizadas (06/2026 - 09/2026)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
DATA_DIR.mkdir(parents=True, exist_ok=True)

SHARED_METADATA = {
    "protocolo": "PII Masking - Ley 25.326 de Proteccion de Datos Personales (Argentina)",
    "titular_sanitizado": "USUARIO_ANON_01",
    "domicilio_sanitizado": "Avda. San Martín 12XX, Salta Capital",
    "responsable_auditoria": "Estudiante UGD (Matricula: 100001)",
    "catedra": "Principios de Inteligencia Artificial (GT110) - UGD 2026"
}

FACTURAS = {
    "06/2026": {
        "metadata_sanitizacion": {
            **SHARED_METADATA,
            "fecha_procesamiento": "2026-06-25T12:00:00Z"
        },
        "bloque_a_identificacion": {
            "nis": "3024***",
            "nro_liquidacion": "0101-52061101",
            "periodo_facturado": "06/2026",
            "fecha_emision": "2026-06-23",
            "fecha_vencimiento": "2026-07-17",
            "proximo_vencimiento": "2026-08-18",
            "fecha_corte_suspension": "2026-07-31",
            "deuda_vencida_pendiente": 0.00,
            "pago_anterior_registrado": 315798.64,
            "total_factura": 439863.51
        },
        "bloque_b_electricidad_edesa": {
            "empresa_distribuidora": "EDESA S.A.",
            "categoria_tarifaria": "T1-R2-SEF",
            "descripcion_categoria": "Tarifa 1 Pequeñas Demandas, Rango 2 Residencial, Servicio Electrico Focalizado",
            "tipo_inmueble_declarado": "RESIDENCIAL",
            "medidor": "1688***",
            "marca_medidor": "LANDIS+GYR",
            "potencia_contratada_kw": 2.0,
            "periodo_lectura": {
                "desde": "2026-05-15",
                "hasta": "2026-06-14",
                "dias": 30
            },
            "energia_activa": {
                "lectura_anterior": 27874.0,
                "lectura_actual": 28592.0,
                "constante": 1.0,
                "consumo_kwh": 718.0
            },
            "energia_reactiva": {
                "lectura_anterior": 10420.0,
                "lectura_actual": 10615.0,
                "constante": 1.0,
                "consumo_kvarh": 195.0
            },
            "factor_potencia_cos_phi": 0.9620,
            "desglose_costos": {
                "cargo_fijo_total": 8450.00,
                "energia_activa_base_200kwh": 34800.00,
                "energia_activa_excedente": 145040.49,
                "iva_consumidor_final_21": 39540.64,
                "subtotal_edesa_neto": 227831.13,
                "incidencia_energia_alumbrado_publico_kwh": 26.50,
                "incidencia_energia_alumbrado_publico_monto": 11019.32,
                "subtotal_con_alumbrado": 238850.45,
                "subsidio_estatal_declarado": 24604.05
            }
        },
        "bloque_c_agua_aguas_del_norte": {
            "empresa_concesionaria": "Aguas del Norte S.A. / CoSAySa",
            "usuario_id": "395**",
            "codigo_servicio": "AGYCL",
            "descripcion_servicio": "Agua Potable y Desagües Cloacales",
            "catastro": "430**",
            "condicion_fiscal": "IVA Sujeto No Categorizado",
            "categoria_uso": "NO RESIDENCIAL 1",
            "tipo_inmueble_declarado": "NO_RESIDENCIAL",
            "medidor": "0000007***",
            "diametro_mm": 19,
            "coeficiente": 1.10,
            "periodo_lectura": {
                "desde": "2026-04-26",
                "hasta": "2026-05-26",
                "dias": 30
            },
            "lecturas_volumen": {
                "lectura_anterior_m3": 4444.0,
                "lectura_actual_m3": 4475.0,
                "consumo_m3": 31.0,
                "rango_m3": "20 a 50 m3",
                "precio_unitario_m3": 1299.787
            },
            "desglose_costos": {
                "cargo_fijo": 62195.22,
                "consumo_variable": 40293.40,
                "tasa_fiscalizacion_enresp_2": 2049.77,
                "iva_no_categorizado_27": 27671.93,
                "percepcion_iva_no_categorizado_13_5": 17571.67,
                "subtotal_aguas_del_norte": 149781.99
            }
        },
        "bloque_d_tributos_municipales_y_concesiones": {
            "municipalidad_de_salta": {
                "tasa_municipal": 40992.56,
                "proteccion_bienes_y_personas": 1116.77,
                "impuesto_inmobiliario": 2608.67,
                "subtotal_municipal": 44718.00
            },
            "lusal_ute": {
                "concepto": "Mantenimiento Alumbrado Publico",
                "tarifa": "C1",
                "subtotal_lusal": 6513.07
            },
            "subtotal_conceptos_municipales_y_externos": 51231.07
        },
        "bloque_e_marco_regulatorio_enresp": {
            "ente_regulador": "Ente Regulador de los Servicios Publicos de Salta (ENRESP)",
            "resolucion_desdoblamiento": "Resolucion ENRESP Nro. 1590/24",
            "derecho_desdoblamiento": True,
            "servicio_esencial_prioritario": "ENERGIA_ELECTRICA",
            "monto_desdoblable_energia": 238850.45,
            "monto_conceptos_desdoblables_excluidos": 201013.06
        }
    },

    "07/2026": {
        "metadata_sanitizacion": {
            **SHARED_METADATA,
            "fecha_procesamiento": "2026-07-28T12:00:00Z"
        },
        "bloque_a_identificacion": {
            "nis": "3024***",
            "nro_liquidacion": "0101-52062202",
            "periodo_facturado": "07/2026",
            "fecha_emision": "2026-07-27",
            "fecha_vencimiento": "2026-08-18",
            "proximo_vencimiento": "2026-09-16",
            "fecha_corte_suspension": "2026-08-31",
            "deuda_vencida_pendiente": 0.00,
            "pago_anterior_registrado": 439863.51,
            "total_factura": 516720.99
        },
        "bloque_b_electricidad_edesa": {
            "empresa_distribuidora": "EDESA S.A.",
            "categoria_tarifaria": "T1-R2-SEF",
            "descripcion_categoria": "Tarifa 1 Pequeñas Demandas, Rango 2 Residencial, Servicio Electrico Focalizado",
            "tipo_inmueble_declarado": "RESIDENCIAL",
            "medidor": "1688***",
            "marca_medidor": "LANDIS+GYR",
            "potencia_contratada_kw": 2.0,
            "periodo_lectura": {
                "desde": "2026-06-15",
                "hasta": "2026-07-15",
                "dias": 30
            },
            "energia_activa": {
                "lectura_anterior": 28592.0,
                "lectura_actual": 29439.0,
                "constante": 1.0,
                "consumo_kwh": 847.0
            },
            "energia_reactiva": {
                "lectura_anterior": 10615.0,
                "lectura_actual": 10838.0,
                "constante": 1.0,
                "consumo_kvarh": 223.0
            },
            "factor_potencia_cos_phi": 0.9580,
            "desglose_costos": {
                "cargo_fijo_total": 8850.00,
                "energia_activa_base_200kwh": 35200.00,
                "energia_activa_excedente": 189950.00,
                "iva_consumidor_final_21": 49148.08,
                "subtotal_edesa_neto": 283148.08,
                "incidencia_energia_alumbrado_publico_kwh": 27.10,
                "incidencia_energia_alumbrado_publico_monto": 11711.39,
                "subtotal_con_alumbrado": 294859.47,
                "subsidio_estatal_declarado": 25688.18
            }
        },
        "bloque_c_agua_aguas_del_norte": {
            "empresa_concesionaria": "Aguas del Norte S.A. / CoSAySa",
            "usuario_id": "395**",
            "codigo_servicio": "AGYCL",
            "descripcion_servicio": "Agua Potable y Desagües Cloacales",
            "catastro": "430**",
            "condicion_fiscal": "IVA Sujeto No Categorizado",
            "categoria_uso": "NO RESIDENCIAL 1",
            "tipo_inmueble_declarado": "NO_RESIDENCIAL",
            "medidor": "0000007***",
            "diametro_mm": 19,
            "coeficiente": 1.10,
            "periodo_lectura": {
                "desde": "2026-05-27",
                "hasta": "2026-06-26",
                "dias": 30
            },
            "lecturas_volumen": {
                "lectura_anterior_m3": 4475.0,
                "lectura_actual_m3": 4511.0,
                "consumo_m3": 36.0,
                "rango_m3": "20 a 50 m3",
                "precio_unitario_m3": 1360.156
            },
            "desglose_costos": {
                "cargo_fijo": 65083.88,
                "consumo_variable": 48965.62,
                "tasa_fiscalizacion_enresp_2": 2280.99,
                "iva_no_categorizado_27": 30793.37,
                "percepcion_iva_no_categorizado_13_5": 19553.79,
                "subtotal_aguas_del_norte": 166677.65
            }
        },
        "bloque_d_tributos_municipales_y_concesiones": {
            "municipalidad_de_salta": {
                "tasa_municipal": 44614.90,
                "proteccion_bienes_y_personas": 1216.77,
                "impuesto_inmobiliario": 2839.13,
                "subtotal_municipal": 48670.80
            },
            "lusal_ute": {
                "concepto": "Mantenimiento Alumbrado Publico",
                "tarifa": "C1",
                "subtotal_lusal": 6513.07
            },
            "subtotal_conceptos_municipales_y_externos": 55183.87
        },
        "bloque_e_marco_regulatorio_enresp": {
            "ente_regulador": "Ente Regulador de los Servicios Publicos de Salta (ENRESP)",
            "resolucion_desdoblamiento": "Resolucion ENRESP Nro. 1590/24",
            "derecho_desdoblamiento": True,
            "servicio_esencial_prioritario": "ENERGIA_ELECTRICA",
            "monto_desdoblable_energia": 294859.47,
            "monto_conceptos_desdoblables_excluidos": 221861.52
        }
    },

    "08/2026": {
        "metadata_sanitizacion": {
            **SHARED_METADATA,
            "fecha_procesamiento": "2026-08-28T12:00:00Z"
        },
        "bloque_a_identificacion": {
            "nis": "3024***",
            "nro_liquidacion": "0101-52063303",
            "periodo_facturado": "08/2026",
            "fecha_emision": "2026-08-26",
            "fecha_vencimiento": "2026-09-16",
            "proximo_vencimiento": "2026-10-16",
            "fecha_corte_suspension": "2026-09-30",
            "deuda_vencida_pendiente": 0.00,
            "pago_anterior_registrado": 516720.99,
            "total_factura": 340064.55
        },
        "bloque_b_electricidad_edesa": {
            "empresa_distribuidora": "EDESA S.A.",
            "categoria_tarifaria": "T1-R2-SEF",
            "descripcion_categoria": "Tarifa 1 Pequeñas Demandas, Rango 2 Residencial, Servicio Electrico Focalizado",
            "tipo_inmueble_declarado": "RESIDENCIAL",
            "medidor": "1688***",
            "marca_medidor": "LANDIS+GYR",
            "potencia_contratada_kw": 2.0,
            "periodo_lectura": {
                "desde": "2026-07-15",
                "hasta": "2026-08-14",
                "dias": 30
            },
            "energia_activa": {
                "lectura_anterior": 29439.0,
                "lectura_actual": 29796.0,
                "constante": 1.0,
                "consumo_kwh": 357.0
            },
            "energia_reactiva": {
                "lectura_anterior": 10838.0,
                "lectura_actual": 10935.0,
                "constante": 1.0,
                "consumo_kvarh": 97.0
            },
            "factor_potencia_cos_phi": 0.9650,
            "desglose_costos": {
                "cargo_fijo_total": 9150.00,
                "energia_activa_base_200kwh": 36100.00,
                "energia_activa_excedente": 34489.83,
                "iva_consumidor_final_21": 16744.86,
                "subtotal_edesa_neto": 96484.69,
                "incidencia_energia_alumbrado_publico_kwh": 27.50,
                "incidencia_energia_alumbrado_publico_monto": 12234.22,
                "subtotal_con_alumbrado": 108718.91,
                "subsidio_estatal_declarado": 29354.77
            }
        },
        "bloque_c_agua_aguas_del_norte": {
            "empresa_concesionaria": "Aguas del Norte S.A. / CoSAySa",
            "usuario_id": "395**",
            "codigo_servicio": "AGYCL",
            "descripcion_servicio": "Agua Potable y Desagües Cloacales",
            "catastro": "430**",
            "condicion_fiscal": "IVA Sujeto No Categorizado",
            "categoria_uso": "NO RESIDENCIAL 1",
            "tipo_inmueble_declarado": "NO_RESIDENCIAL",
            "medidor": "0000007***",
            "diametro_mm": 19,
            "coeficiente": 1.10,
            "periodo_lectura": {
                "desde": "2026-06-27",
                "hasta": "2026-07-26",
                "dias": 30
            },
            "lecturas_volumen": {
                "lectura_anterior_m3": 4511.0,
                "lectura_actual_m3": 4548.0,
                "consumo_m3": 37.0,
                "rango_m3": "20 a 50 m3",
                "precio_unitario_m3": 1420.608
            },
            "desglose_costos": {
                "cargo_fijo": 67976.53,
                "consumo_variable": 52562.50,
                "tasa_fiscalizacion_enresp_2": 2410.78,
                "iva_no_categorizado_27": 32545.54,
                "percepcion_iva_no_categorizado_13_5": 20666.42,
                "subtotal_aguas_del_norte": 176161.77
            }
        },
        "bloque_d_tributos_municipales_y_concesiones": {
            "municipalidad_de_salta": {
                "tasa_municipal": 44614.90,
                "proteccion_bienes_y_personas": 1216.77,
                "impuesto_inmobiliario": 2839.13,
                "subtotal_municipal": 48670.80
            },
            "lusal_ute": {
                "concepto": "Mantenimiento Alumbrado Publico",
                "tarifa": "C1",
                "subtotal_lusal": 6513.07
            },
            "subtotal_conceptos_municipales_y_externos": 55183.87
        },
        "bloque_e_marco_regulatorio_enresp": {
            "ente_regulador": "Ente Regulador de los Servicios Publicos de Salta (ENRESP)",
            "resolucion_desdoblamiento": "Resolucion ENRESP Nro. 1590/24",
            "derecho_desdoblamiento": True,
            "servicio_esencial_prioritario": "ENERGIA_ELECTRICA",
            "monto_desdoblable_energia": 108718.91,
            "monto_conceptos_desdoblables_excluidos": 231345.64
        }
    },

    "09/2026": {
        "metadata_sanitizacion": {
            **SHARED_METADATA,
            "fecha_procesamiento": "2026-10-04T12:00:00Z"
        },
        "bloque_a_identificacion": {
            "nis": "3024***",
            "nro_liquidacion": "0101-52064404",
            "periodo_facturado": "09/2026",
            "fecha_emision": "2026-09-22",
            "fecha_vencimiento": "2026-10-16",
            "proximo_vencimiento": "2026-11-17",
            "fecha_corte_suspension": "2026-10-30",
            "deuda_vencida_pendiente": 0.00,
            "pago_anterior_registrado": 340064.55,
            "total_factura": 377559.51
        },
        "bloque_b_electricidad_edesa": {
            "empresa_distribuidora": "EDESA S.A.",
            "categoria_tarifaria": "T1-R2-SEF",
            "descripcion_categoria": "Tarifa 1 Pequeñas Demandas, Rango 2 Residencial, Servicio Electrico Focalizado",
            "tipo_inmueble_declarado": "RESIDENCIAL",
            "medidor": "1688***",
            "marca_medidor": "LANDIS+GYR",
            "potencia_contratada_kw": 2.0,
            "periodo_lectura": {
                "desde": "2026-08-14",
                "hasta": "2026-09-14",
                "dias": 31
            },
            "energia_activa": {
                "lectura_anterior": 29796.0,
                "lectura_actual": 30224.0,
                "constante": 1.0,
                "consumo_kwh": 428.0
            },
            "energia_reactiva": {
                "lectura_anterior": 10813.0,
                "lectura_actual": 10930.0,
                "constante": 1.0,
                "consumo_kvarh": 117.0
            },
            "factor_potencia_cos_phi": 0.9644,
            "desglose_costos": {
                "cargo_fijo_tramo1": 5126.97,
                "cargo_fijo_tramo2": 4355.76,
                "cargo_fijo_total": 9482.73,
                "energia_activa_base_200kwh": 37418.36,
                "energia_activa_excedente_tramo1_35kwh": 10414.91,
                "energia_activa_excedente_tramo2_193kwh": 58263.25,
                "iva_consumidor_final_21": 24271.64,
                "subtotal_edesa_neto": 139850.89,
                "incidencia_energia_alumbrado_publico_kwh": 27.986,
                "incidencia_energia_alumbrado_publico_monto": 12597.08,
                "subtotal_con_alumbrado": 152447.97,
                "subsidio_estatal_declarado": 20185.95
            }
        },
        "bloque_c_agua_aguas_del_norte": {
            "empresa_concesionaria": "Aguas del Norte S.A. / CoSAySa",
            "usuario_id": "395**",
            "codigo_servicio": "AGYCL",
            "descripcion_servicio": "Agua Potable y Desagües Cloacales",
            "catastro": "430**",
            "condicion_fiscal": "IVA Sujeto No Categorizado",
            "categoria_uso": "NO RESIDENCIAL 1",
            "tipo_inmueble_declarado": "NO_RESIDENCIAL",
            "medidor": "0000007***",
            "diametro_mm": 19,
            "coeficiente": 1.10,
            "periodo_lectura": {
                "desde": "2026-07-27",
                "hasta": "2026-08-26",
                "dias": 30
            },
            "lecturas_volumen": {
                "lectura_anterior_m3": 4548.0,
                "lectura_actual_m3": 4580.0,
                "consumo_m3": 32.0,
                "rango_m3": "20 a 50 m3",
                "precio_unitario_m3": 1450.441
            },
            "desglose_costos": {
                "cargo_fijo": 69404.04,
                "consumo_variable": 46414.10,
                "tasa_fiscalizacion_enresp_2": 2316.36,
                "iva_no_categorizado_27": 31270.90,
                "percepcion_iva_no_categorizado_13_5": 19857.02,
                "subtotal_aguas_del_norte": 169262.42
            }
        },
        "bloque_d_tributos_municipales_y_concesiones": {
            "municipalidad_de_salta": {
                "tasa_municipal": 44614.90,
                "proteccion_bienes_y_personas": 1216.77,
                "impuesto_inmobiliario": 2839.13,
                "subtotal_municipal": 48670.80
            },
            "lusal_ute": {
                "concepto": "Mantenimiento Alumbrado Publico",
                "tarifa": "C1",
                "subtotal_lusal": 7178.32
            },
            "subtotal_conceptos_municipales_y_externos": 55849.12
        },
        "bloque_e_marco_regulatorio_enresp": {
            "ente_regulador": "Ente Regulador de los Servicios Publicos de Salta (ENRESP)",
            "resolucion_desdoblamiento": "Resolucion ENRESP Nro. 1590/24",
            "derecho_desdoblamiento": True,
            "servicio_esencial_prioritario": "ENERGIA_ELECTRICA",
            "monto_desdoblable_energia": 152447.97,
            "monto_conceptos_desdoblables_excluidos": 225111.54
        }
    }
}


def main():
    # 1. Guardar facturas individuales
    for period, inv in FACTURAS.items():
        fname = f"factura_{period.replace('/', '_')}.json"
        fpath = DATA_DIR / fname
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(inv, f, indent=2, ensure_ascii=False)
        print(f"[OK] Guardada factura individual: {fname}")

    # 2. Guardar dataset consolidado facturas_historico.json
    dataset_consolidado = {
        "descripcion": "Serie Histórica Multimes Auditada de Facturas de Salta (EDESA + Aguas del Norte)",
        "suministro": {
            "nis": "3024***",
            "titular": "USUARIO_ANON_01",
            "domicilio": "Avda. San Martín 12XX, Salta Capital",
            "localidad": "Salta Capital, Provincia de Salta",
            "tarifa_edesa": "T1-R2-SEF (Residencial)",
            "tarifa_aguas": "NO RESIDENCIAL 1"
        },
        "periodos": list(FACTURAS.keys()),
        "facturas": [FACTURAS[p] for p in FACTURAS],
        "facturas_por_periodo": FACTURAS
    }

    historico_path = DATA_DIR / "facturas_historico.json"
    with open(historico_path, "w", encoding="utf-8") as f:
        json.dump(dataset_consolidado, f, indent=2, ensure_ascii=False)
    print(f"[OK] Guardado histórico consolidado: {historico_path.name}")


if __name__ == "__main__":
    main()
