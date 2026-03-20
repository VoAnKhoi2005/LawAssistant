import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:law_assistant_kg/src/core/app.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('App renders without crashing', (tester) async {
    tester.binding.window.physicalSizeTestValue = const Size(1440, 900);
    tester.binding.window.devicePixelRatioTestValue = 1.0;

    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });

    await tester.pumpWidget(const App());

    expect(find.byType(App), findsOneWidget);
  });
}
