# Documentación de Requisitos - Sistema de Gestión de Pago de Agua

## 1. Tecnologías a Usar

-   **Framework principal**: [Electron](https://www.electronjs.org/)
    (aplicación de escritorio offline).
-   **Base de datos**: SQLite (local, liviana y suficiente para los
    datos).
-   **Frontend**: Tailwind CSS (para estilos simples, limpios y con
    animaciones suaves).
-   **Animaciones**: Transiciones limpias, especialmente en menú
    lateral.

## 2. Seguridad y Acceso

-   **Login**:
    -   Un solo **administrador**.
    -   Acceso mediante **PIN numérico**.
-   No se requieren múltiples roles de usuario.

## 3. Gestión de Clientes

-   **Registro**:
    -   Se podrán agregar clientes manualmente desde la aplicación.
    -   Datos obligatorios:
        -   Nombre completo.
        -   Dirección.
        -   ID autogenerado único.
        -   Estado (activo/inactivo).
-   **Identificación de clientes**:
    -   El sistema autogenerará un ID único incremental (no editable).
    -   Búsqueda de clientes:
        -   En tiempo real (mientras se escribe).
        -   Por **nombre**.
        -   Por **dirección**.
        -   Por **ID** (si se conoce).

## 4. Dashboard Principal

-   **Vista general** de los clientes:
    -   Nombre, dirección, estado de pago (✅ Pagado / ❌ Pendiente / 💧
        Exceso de consumo).
-   **Filtros**:
    -   Ver solo clientes con deuda.
    -   Ver solo clientes al corriente.
-   **Botón de cambio de vista**: Tabla ↔ Gráficas simples.

## 5. Calendario

-   Incluido en el dashboard.
-   Permite al admin **consultar por fechas**:
    -   Quién pagó.
    -   Quién debe.
    -   Quién tiene exceso de consumo.

## 6. Perfil del Cliente

Al abrir un cliente desde el buscador o el dashboard, se mostrará: -
Datos completos: Nombre, dirección, ID, estado. - Historial de pagos: -
Montos. - Fechas exactas. - Estado del pago. - Consumo de agua: -
Normal. - Exceso (con registro en caso de desperdicio o sobrecarga). -
Opciones: - Editar datos. - Actualizar pagos. - Marcar exceso de
consumo.

## 7. Funciones Extra

-   **Historial completo** de cada cliente (no se borra nada, solo se
    actualiza con nuevos registros).
-   **Indicador de consumo extra** en caso de desperdicio de agua.
-   **Menú lateral** con animaciones limpias:
    -   Dashboard.
    -   Clientes.
    -   Calendario.
    -   Ajustes.

## 8. Estilo y Usabilidad

-   Diseño **simple pero funcional**.
-   Uso de **Tailwind CSS**.
-   Animaciones limpias para transiciones y menú lateral.
-   Interfaz amigable para un **solo administrador**.

------------------------------------------------------------------------

✅ Este documento reúne **todos los requisitos solicitados** y sirve
como guía completa para que un agente IA pueda desarrollar el sistema.
