import React, { useState, useRef } from 'react';
import './ImageUploader.css';

interface ImageUploaderProps {
    onUpload: (file: File) => void;
    isUploading?: boolean;
    title?: string;
    description?: string;
    uploadText?: string;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
    onUpload,
    isUploading = false,
    title = "Upload Your Solution",
    description = "Drag and drop your image here, or click to browse",
    uploadText = "Processing your solution..."
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const [preview, setPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files[0]) {
            handleFile(files[0]);
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files[0]) {
            handleFile(files[0]);
        }
    };

    const handleFile = (file: File) => {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file (JPEG or PNG)');
            return;
        }

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);

        // Call upload handler
        onUpload(file);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="image-uploader">
            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="image-uploader__input"
            />

            <div
                className={`image-uploader__dropzone ${isDragging ? 'image-uploader__dropzone--dragging' : ''} ${preview ? 'image-uploader__dropzone--has-preview' : ''}`}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                {isUploading ? (
                    <div className="image-uploader__uploading">
                        <div className="loading" style={{ width: '40px', height: '40px' }}></div>
                        <p>{uploadText}</p>
                    </div>
                ) : preview ? (
                    <div className="image-uploader__preview">
                        <img src={preview} alt="Preview" />
                        <p className="image-uploader__preview-text">Click or drag to upload a different image</p>
                    </div>
                ) : (
                    <div className="image-uploader__placeholder">
                        <div className="image-uploader__icon">📸</div>
                        <h3>{title}</h3>
                        <p>{description}</p>
                        <span className="image-uploader__formats">Supports: JPEG, PNG</span>
                    </div>
                )}
            </div>
        </div>
    );
};
