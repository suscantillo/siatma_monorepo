import 'package:app/color_schemes.g.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

// Main App widget
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SIATMA App',
      theme: ThemeData(useMaterial3: true, colorScheme: flexSchemeLight),
      darkTheme: ThemeData(useMaterial3: true, colorScheme: flexSchemeDark),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0; // State for Bottom Navigation Bar

  // Function to show custom SnackBar notifications
  void _showNotification(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(11)),
        margin: const EdgeInsets.all(10),
      ),
    );
  }

  // List of screens for the Bottom Navigation Bar
  static final List<Widget> _widgetOptions = <Widget>[
    _HomeScreen(), // The actual home screen content
    const Center(child: Text('Mis Reportes', style: TextStyle(fontSize: 24))),
    const Center(child: Text('Mis Alertas', style: TextStyle(fontSize: 24))),
    const Center(
      child: Text('Perfil / Configuración', style: TextStyle(fontSize: 24)),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // App Bar for SIATMA title and menu button
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            border: Border(
              bottom: BorderSide(
                color: Theme.of(context).colorScheme.primary,
                width: 2.0,
              ),
            ),
          ),
        ),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset(
              'assets/images/logo.png', // Path to your logo
              height: 40, // Adjust height as needed
            ),
            // Space between logo and title
            const SizedBox(width: 8), // Add some space between logo and title
            Text(
              'SIATMA',
              style: TextStyle(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        centerTitle: true, // Align to the center
        /* actions: [
          IconButton(
            icon: Icon(
              Icons.menu,
              color: Theme.of(context).colorScheme.onSurface,
            ),
            onPressed: () {
              // Action for menu button
              _showNotification('Menú presionado');
            },
          ),
        ], */
      ),
      body: _widgetOptions.elementAt(
        _selectedIndex,
      ), // Display the selected screen
      // Floating Action Button for reporting incidents
      floatingActionButton: _selectedIndex == 0
          ? FloatingActionButton(
              onPressed: () {
                // Navigate to Report Incident screen
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ReportIncidentPage(),
                  ),
                );
              },
              backgroundColor: Theme.of(context).colorScheme.primary,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30.0),
              ),
              elevation: 6,
              child: Icon(
                Icons.add,
                color: Theme.of(context).colorScheme.onPrimary,
                size: 30,
              ),
            )
          : null,
      floatingActionButtonLocation:
          FloatingActionButtonLocation.endFloat, // Position FAB
      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        items: <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: const Icon(Icons.home_outlined),
            activeIcon: Icon(
              Icons.home,
              color: Theme.of(context).colorScheme.primary,
            ),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.description_outlined),
            activeIcon: Icon(
              Icons.description,
              color: Theme.of(context).colorScheme.primary,
            ),
            label: 'Mis Reportes',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.notifications_outlined),
            activeIcon: Icon(
              Icons.notifications,
              color: Theme.of(context).colorScheme.primary,
            ),
            label: 'Mis Alertas',
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_outline),
            activeIcon: Icon(
              Icons.person,
              color: Theme.of(context).colorScheme.primary,
            ),
            label: 'Perfil',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Theme.of(context).colorScheme.primary,
        unselectedItemColor: Theme.of(context).colorScheme.onSurface,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
            if (index != 0) {
              // For non-home tabs, show a notification that it's not implemented
              _showNotification(
                'Funcionalidad "${['Inicio', 'Mis Reportes', 'Mis Alertas', 'Perfil'][index]}" no implementada en este ejemplo.',
              );
            }
          });
        },
        type: BottomNavigationBarType.fixed, // Ensures all labels are visible
        backgroundColor: Theme.of(context).colorScheme.surface,
        elevation: 8,
        showUnselectedLabels: true,
      ),
    );
  }
}

// Home Screen content widget (Map and Alerts view)
class _HomeScreen extends StatelessWidget {
  // Notification utility function
  void _showNotification(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(10),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search Bar
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: TextField(
            decoration: InputDecoration(
              hintText: 'Buscar ubicación o alerta...',
              prefixIcon: Icon(
                Icons.search,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12.0),
                borderSide: BorderSide.none,
              ),
              filled: true,
              fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
            ),
          ),
        ),
        // Priority Alert Banner
        Container(
          width: double.infinity,
          color: Theme.of(context).colorScheme.error,
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Expanded(
                child: Text(
                  '¡Alerta Crítica! Inundación en el sector Los Almendros.',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              GestureDetector(
                onTap: () {
                  _showNotification(
                    context,
                    'Detalles de la alerta crítica...',
                  );
                },
                child: const Text(
                  'Ver detalles',
                  style: TextStyle(
                    color: Colors.white,
                    decoration: TextDecoration.underline,
                    fontSize: 13,
                  ),
                ),
              ),
            ],
          ),
        ),
        // Map Placeholder
        Expanded(
          child: Stack(
            children: [
              // Placeholder image for the map
              Image.network(
                'https://placehold.co/400x600/aabbcc/ffffff?text=Mapa+Interactivo',
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
                errorBuilder: (context, error, stackTrace) => Container(
                  color: Colors.grey[300],
                  child: const Center(
                    child: Text(
                      'Mapa Interactivo',
                      style: TextStyle(color: Colors.grey, fontSize: 20),
                    ),
                  ),
                ),
              ),
              // Map Controls
              Positioned(
                top: 16,
                right: 16,
                child: Column(
                  children: [
                    _MapControlButton(
                      icon: Icons.my_location,
                      onPressed: () =>
                          _showNotification(context, 'Centrar ubicación'),
                    ),
                    const SizedBox(height: 8),
                    _MapControlButton(
                      icon: Icons.add,
                      onPressed: () => _showNotification(context, 'Zoom In'),
                    ),
                    const SizedBox(height: 8),
                    _MapControlButton(
                      icon: Icons.remove,
                      onPressed: () => _showNotification(context, 'Zoom Out'),
                    ),
                    const SizedBox(height: 8),
                    _MapControlButton(
                      icon: Icons.layers,
                      onPressed: () =>
                          _showNotification(context, 'Capas del mapa'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// Helper widget for map control buttons
class _MapControlButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;

  const _MapControlButton({required this.icon, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24.0)),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(24.0),
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Icon(
            icon,
            color: Theme.of(context).colorScheme.onSurface,
            size: 24,
          ),
        ),
      ),
    );
  }
}

// Report Incident Screen widget
class ReportIncidentPage extends StatefulWidget {
  const ReportIncidentPage({super.key});

  @override
  State<ReportIncidentPage> createState() => _ReportIncidentPageState();
}

class _ReportIncidentPageState extends State<ReportIncidentPage> {
  final _formKey = GlobalKey<FormState>();
  String? _selectedReportType;
  final TextEditingController _descriptionController = TextEditingController();
  String _location =
      'Presiona el ícono para obtener tu ubicación'; // Placeholder for location
  bool _isGettingLocation = false;
  final List<String> _photoUrls =
      []; // To store URLs of selected photos (simulated)
  bool _isOffline = false; // Simulated offline mode

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
    // Simulate offline status
    Future.delayed(const Duration(milliseconds: 100), () {
      setState(() {
        _isOffline = false; // Start online for the example
      });
    });
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  void _showNotification(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(10),
      ),
    );
  }

  Future<void> _getCurrentLocation() async {
    setState(() {
      _isGettingLocation = true;
    });

    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _showNotification('Los permisos de ubicación están denegados.');
          setState(() {
            _location = 'Permisos de ubicación denegados.';
            _isGettingLocation = false;
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        _showNotification(
            'Los permisos de ubicación están denegados permanentemente, no podemos solicitar permisos.');
        setState(() {
          _location = 'Permisos de ubicación denegados permanentemente.';
          _isGettingLocation = false;
        });
        return;
      }

      final position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high);
      setState(() {
        _location = 'Lat: ${position.latitude}, Lon: ${position.longitude}';
        _isGettingLocation = false;
      });
    } catch (e) {
      _showNotification('No se pudo obtener la ubicación: $e');
      setState(() {
        _location = 'Error al obtener la ubicación.';
        _isGettingLocation = false;
      });
    }
  }

  void _handleReportSubmit() {
    if (_formKey.currentState?.validate() ?? false) {
      // Simulate sending data or saving offline
      _showNotification('¡Reporte enviado con éxito!');
      print('Tipo de Reporte: $_selectedReportType');
      print('Descripción: ${_descriptionController.text}');
      print('Ubicación: $_location');
      print('Fotos: $_photoUrls');

      // Navigate back to home screen
      Navigator.pop(context);
    }
  }

  void _handlePhotoUpload() {
    // In a real app, use image_picker package here
    // For this example, we'll just add a placeholder image
    setState(() {
      _photoUrls.add('https://placehold.co/100x100/eeeeee/333333?text=Foto');
    });
    _showNotification('Imagen seleccionada (simulada)');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Theme.of(context).colorScheme.primary,
                Theme.of(context).colorScheme.primaryContainer,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        title: Text(
          'Reportar Incidente',
          style: TextStyle(
            color: Theme.of(context).colorScheme.onPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: Icon(
            Icons.arrow_back,
            color: Theme.of(context).colorScheme.onPrimary,
          ),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Offline Indicator
              if (_isOffline)
                Container(
                  padding: const EdgeInsets.all(12.0),
                  margin: const EdgeInsets.only(bottom: 16.0),
                  decoration: BoxDecoration(
                    color: Colors.yellow[100],
                    border: Border(
                      left: BorderSide(color: Colors.yellow[700]!, width: 4),
                    ),
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Modo Offline:',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.yellow[800],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'El reporte se guardará localmente y se sincronizará cuando haya conexión.',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.yellow[800],
                        ),
                      ),
                    ],
                  ),
                ),
              // Type of Incident Dropdown
              Text(
                'Tipo de Incidente *',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedReportType,
                hint: const Text('Selecciona un tipo'),
                decoration: const InputDecoration(
                  // Applying the input decoration from theme
                ),
                items:
                    <String>[
                      'Grietas en el terreno',
                      'Deslizamiento menor',
                      'Inundación',
                      'Cambio en el caudal del río',
                      'Sequía',
                      'Otro',
                    ].map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedReportType = newValue;
                  });
                },
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor, selecciona un tipo de incidente.';
                  }
                  return null;
                },
                dropdownColor: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              const SizedBox(height: 16),

              // Description Textarea
              Text(
                'Descripción *',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _descriptionController,
                maxLines: 4,
                decoration: const InputDecoration(
                  hintText: 'Describe el incidente en detalle...',
                  // Applying the input decoration from theme
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor, ingresa una descripción.';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Location Input
              Text(
                'Ubicación',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              TextFormField(
                // Use a key to force the widget to rebuild when the initialValue changes
                key: Key(_location),
                readOnly: true,
                initialValue:
                    _isGettingLocation ? 'Obteniendo ubicación...' : _location,
                decoration: InputDecoration(
                  // Applying the input decoration from theme
                  suffixIcon: _isGettingLocation
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: Padding(
                            padding: EdgeInsets.all(8.0),
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          ),
                        )
                      : IconButton(
                          icon: const Icon(Icons.gps_fixed),
                          onPressed: _getCurrentLocation,
                        ),
                ),
              ),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () {
                    _showNotification(
                      'Función para ajustar ubicación manualmente (no implementada en este ejemplo).',
                    );
                  },
                  child: const Text('Ajustar manualmente en el mapa'),
                ),
              ),
              const SizedBox(height: 16),

              // Photo Evidence Section
              Text(
                'Evidencia Fotográfica',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ElevatedButton.icon(
                onPressed: _handlePhotoUpload,
                icon: const Icon(Icons.camera_alt, color: Colors.blue),
                label: const Text(
                  'Añadir Foto',
                  style: TextStyle(color: Colors.blue),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[50], // Light blue background
                  foregroundColor: Colors.blue[700], // Text color
                  elevation: 0,
                  side: const BorderSide(color: Colors.blue, width: 1),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8.0, // horizontal spacing between photos
                runSpacing: 8.0, // vertical spacing between rows of photos
                children: _photoUrls.map((url) {
                  return ClipRRect(
                    borderRadius: BorderRadius.circular(8.0),
                    child: Image.network(
                      url,
                      width: 90,
                      height: 90,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) => Container(
                        width: 90,
                        height: 90,
                        color: Colors.grey[200],
                        child: const Icon(
                          Icons.broken_image,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Submit and Cancel Buttons
              ElevatedButton(
                onPressed: _handleReportSubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green[600], // Green button
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50), // Full width
                ),
                child: const Text('Enviar Reporte'),
              ),
              const SizedBox(height: 8),
              OutlinedButton(
                onPressed: () => Navigator.pop(context),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.grey[700],
                  minimumSize: const Size(double.infinity, 50), // Full width
                  side: BorderSide(color: Colors.grey[400]!),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                ),
                child: const Text('Cancelar'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
