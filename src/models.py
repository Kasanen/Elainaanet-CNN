"""Mallit A, B, C1 ja C2 (T07, T08, T10, T12)."""

import keras


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
