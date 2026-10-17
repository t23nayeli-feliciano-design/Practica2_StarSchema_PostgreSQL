import pandas as pd
import numpy as np

# 1. Simulación de Ingesta Operativa (OLTP)
np.random.seed(101)
n = 500

df_operativo = pd.DataFrame({
    'id_transaccion': range(1000, 1000 + n),
    'fecha_hora': pd.date_range(start='2026-01-01', periods=n, freq='h'),
    'cliente_nombre': np.random.choice(['Juan Pérez', 'María Gómez', 'Carlos Ruiz'], n),
    'cliente_ciudad': np.random.choice(['Puebla', 'CDMX', 'Guadalajara'], n),
    'producto_nombre': np.random.choice(['Laptop Dell', 'Mouse Logi', 'Monitor LG'], n),
    'categoria_prod': np.random.choice(['Cómputo', 'Accesorios', 'Pantallas'], n),
    'precio_unitario': np.random.choice([15000.0, 350.0, 4500.0], n),
    'cantidad': np.random.randint(1, 5, n)
})

# 2. Construcción de Dimensión Cliente (Dim_Cliente)
dim_cliente = df_operativo[['cliente_nombre', 'cliente_ciudad']].drop_duplicates().reset_index(drop=True)
dim_cliente['id_cliente_sk'] = dim_cliente.index + 1  # Surrogate Key

# 3. Construcción de Dimensión Producto (Dim_Producto)
dim_producto = df_operativo[['producto_nombre', 'categoria_prod', 'precio_unitario']].drop_duplicates().reset_index(drop=True)
dim_producto['id_producto_sk'] = dim_producto.index + 1  # Surrogate Key

# 4. Construcción de Dimensión Tiempo (Dim_Tiempo) [EXTENDIDA]
dim_tiempo = pd.DataFrame({'fecha_completa': df_operativo['fecha_hora'].dt.date.unique()})
dim_tiempo['fecha_completa'] = pd.to_datetime(dim_tiempo['fecha_completa'])
dim_tiempo['id_tiempo_sk'] = dim_tiempo['fecha_completa'].dt.strftime('%Y%m%d').astype(int)
dim_tiempo['anio'] = dim_tiempo['fecha_completa'].dt.year
dim_tiempo['mes'] = dim_tiempo['fecha_completa'].dt.month
dim_tiempo['dia'] = dim_tiempo['fecha_completa'].dt.day

# Atributos extendidos para análisis multidimensional
dim_tiempo['dia_semana'] = dim_tiempo['fecha_completa'].dt.day_name()
dim_tiempo['es_fin_semana'] = dim_tiempo['fecha_completa'].dt.dayofweek.isin([5, 6]).astype(int)

# 5. Construcción de Tabla de Hechos (Fact_Ventas) [EXTENDIDA]
fact_ventas = df_operativo.merge(dim_cliente, on=['cliente_nombre', 'cliente_ciudad']) \
                         .merge(dim_producto, on=['producto_nombre', 'categoria_prod', 'precio_unitario'])

fact_ventas['fecha_completa'] = pd.to_datetime(fact_ventas['fecha_hora'].dt.date)
fact_ventas = fact_ventas.merge(dim_tiempo, on='fecha_completa')

# Cálculos de Métricas
fact_ventas['monto_subtotal'] = fact_ventas['cantidad'] * fact_ventas['precio_unitario']
fact_ventas['impuesto_iva'] = (fact_ventas['monto_subtotal'] * 0.16).round(2)
fact_ventas['monto_total_con_iva'] = (fact_ventas['monto_subtotal'] + fact_ventas['impuesto_iva']).round(2)

# Selección de la estructura final del Esquema Estrella
fact_table = fact_ventas[[
    'id_transaccion', 
    'id_cliente_sk', 
    'id_producto_sk', 
    'id_tiempo_sk', 
    'cantidad', 
    'monto_subtotal', 
    'impuesto_iva', 
    'monto_total_con_iva'
]]

# 6. Muestra de Resultados en Consola
print("==================================================")
print("=== DIMENSIÓN CLIENTE (DIM_CLIENTE) ===")
print("==================================================")
print(dim_cliente.head())

print("\n==================================================")
print("=== DIMENSIÓN PRODUCTO (DIM_PRODUCTO) ===")
print("==================================================")
print(dim_producto.head())

print("\n==================================================")
print("=== DIMENSIÓN TIEMPO EXTENDIDA (DIM_TIEMPO) ===")
print("==================================================")
print(dim_tiempo.head())

print("\n==================================================")
print("=== TABLA DE HECHOS EXTENDIDA (FACT_VENTAS) ===")
print("==================================================")
print(fact_table.head())
