"""Mallit A, B, C1 ja C2 (T07, T08, T10, T12)."""

import keras


def build_a(input_shape=(128, 431, 1), n_classes=10, filters=(16, 32, 64, 128), dense=64, lr=1e-3):
    """Malli A (T07): baseline-CNN log-mel-spektrogrammeille.

    len(filters) × [Conv2D(f, 3×3, relu, same) -> MaxPool(2×2)] -> GlobalAveragePooling2D
    -> Dense(dense, relu) -> Dense(n_classes, softmax).
    Ei BatchNormia, Dropoutia eikä L2:ta (ne ja augmentaatio ovat mallissa B), jotta A:n ja
    B:n ero mittaa niiden vaikutusta. GlobalAveragePooling Flattenin sijaan: Flatten antaisi
    noin 1,7 miljoonaa parametria ensimmäiseen Dense-kerrokseen, kun opetusleikkeitä on 240.
    Syöte tulee `src.data.fold_arrays`-funktiosta. Käännetty: Adam(lr),
    sparse_categorical_crossentropy, accuracy.
    """
    layers = [keras.Input(input_shape)]
    for f in filters:
        layers += [keras.layers.Conv2D(f, 3, padding="same", activation="relu"),
                   keras.layers.MaxPooling2D(2)]
    layers += [keras.layers.GlobalAveragePooling2D(),
               keras.layers.Dense(dense, activation="relu"),
               keras.layers.Dense(n_classes, activation="softmax")]

    model = keras.Sequential(layers, name="A")
    model.compile(optimizer=keras.optimizers.Adam(lr),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_c1(input_dim, n_classes=10, hidden=256, dropout=0.5, l2=1e-4, lr=1e-3):
    """Malli C1 (T10): pieni luokitin YAMNet-upotusten päälle.

    Input(input_dim) -> Dense(hidden, relu, L2) -> Dropout -> Dense(n_classes, softmax).
    `hidden=0` jättää piilokerroksen ja Dropoutin pois, jolloin malli on pelkkä
    lineaarinen luokitin (logistinen regressio) vertailukohdaksi. Opetusleikkeitä on
    vain 240 per ajo, joten Dropout ja L2 ovat oletuksena vahvoja.
    Käännetty: Adam(lr), sparse_categorical_crossentropy, accuracy.
    """
    reg = keras.regularizers.l2(l2) if l2 else None
    layers = [keras.Input((input_dim,))]
    if hidden:
        layers += [keras.layers.Dense(hidden, activation="relu", kernel_regularizer=reg),
                   keras.layers.Dropout(dropout)]
    layers.append(keras.layers.Dense(n_classes, activation="softmax", kernel_regularizer=reg))

    model = keras.Sequential(layers, name="C1")
    model.compile(optimizer=keras.optimizers.Adam(lr),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model
