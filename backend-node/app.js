require("dotenv").config();

const express = require("express");
const app = express();

app.use(express.json());

// ---- Todos los módulos de Horisoft, montados en un solo servidor ----
const zonasComunesRoutes = require("./routes/zonasComunes.routes");
const reservasRoutes = require("./routes/reservas.routes");
const vigilantesRoutes = require("./routes/vigilantes.routes");
const visitantesRoutes = require("./routes/visitantes.routes");
const authRoutes = require("./routes/authRoutes");
const usuariosRoutes = require("./routes/usuarios.routes");
const pqrRoutes = require("./routes/pqr.routes");
const comunicadosRoutes = require("./routes/comunicados.routes");
const cuentasCobroRoutes = require("./routes/cuentasCobro.routes");
const pagosRoutes = require("./routes/pagos.routes");
const proveedoresRoutes = require("./routes/proveedores.routes");
const inventarioRoutes = require("./routes/inventario.routes");
const vehiculosRoutes = require("./routes/vehiculos.routes");
const documentosRoutes = require("./routes/documentos.routes");
const configuracionRoutes = require("./routes/configuracion.routes");

app.use("/zonas-comunes", zonasComunesRoutes);
app.use("/reservas", reservasRoutes);
app.use("/vigilantes", vigilantesRoutes);
app.use("/visitantes", visitantesRoutes);
app.use("/auth", authRoutes);
app.use("/usuarios", usuariosRoutes);
app.use("/pqr", pqrRoutes);
app.use("/comunicados", comunicadosRoutes);
app.use("/cuentas-cobro", cuentasCobroRoutes);
app.use("/pagos", pagosRoutes);
app.use("/proveedores", proveedoresRoutes);
app.use("/inventario", inventarioRoutes);
app.use("/vehiculos", vehiculosRoutes);
app.use("/documentos", documentosRoutes);
app.use("/configuracion", configuracionRoutes);

// Ruta raíz informativa
app.get("/", (req, res) => {
    res.json({
        proyecto: "HORISOFT",
        endpoints: {
            zonasComunes: "/zonas-comunes",
            reservas: "/reservas",
            vigilantes: "/vigilantes",
            visitantes: "/visitantes",
            auth: "/auth",
            usuarios: "/usuarios",
            pqr: "/pqr",
            comunicados: "/comunicados",
            cuentasCobro: "/cuentas-cobro",
            pagos: "/pagos",
            proveedores: "/proveedores",
            inventario: "/inventario",
            vehiculos: "/vehiculos",
            documentos: "/documentos",
            configuracion: "/configuracion"
        }
    });
});

// Manejo de rutas no encontradas (404)
app.use((req, res) => {
    res.status(404).json({ mensaje: "Recurso no encontrado" });
});

// Manejo de errores no controlados (500)
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ mensaje: "Error interno del servidor" });
});

// app.js SOLO configura Express (middlewares, rutas, manejo de errores).
// No arranca el servidor: eso es responsabilidad de server.js (punto de
// entrada dedicado), siguiendo el principio de Separación de
// Responsabilidades también a nivel de arranque de la aplicación.
module.exports = app;
